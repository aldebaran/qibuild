## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import Queue
import threading
import sys
import StringIO
import traceback
import time

import qibuild.project

from qisys import ui


class BuildJob(object):
    def __init__(self, project):
        self.project = project
        self.index = 0
        self.num_projects = 0
        # forward dependencies (children this project depends on)
        self.deps = []
        # backward dependencies (parents which depend on this project)
        self.back_deps = []
        # lock which protects deps and back_deps lists
        self.lock = threading.Lock()

    def __str__(self):
        return "<BuildJob %s>" % self.project.name

    def add_dependency(self, job):
        with self.lock:
            self.deps.append(job)
            job._add_back_dependency(self)

    def _add_back_dependency(self, job):
        self.back_deps.append(job)

    def execute(self, *args, **kwargs):
        ui.info_count(self.index, self.num_projects,
                ui.green, "Building",
                ui.blue, self.project.name,
                ui.green, "in",
                ui.blue, self.project.build_type,
                update_title=True)

        self.project.build(**kwargs)

        # job ended, say that to dependants
        with self.lock:
            for parent_job in self.back_deps:
                ui.debug("Signaling end to job", ui.reset, ui.bold, parent_job.project.name)
                parent_job.on_dependent_job_finished(self)

    def on_dependent_job_finished(self, job):
        with self.lock:
            try:
                self.deps.remove(job)
            except ValueError:
                ui.debug(ui.red, "Job not in the deps list!", self.deps, job)
                pass


class ParallelBuilder(object):
    def __init__(self):
        self.all_jobs = []
        self.pending_jobs = []
        self.running_jobs = Queue.Queue()
        self._workers = list()
        self.failed_project = None
        self.job_current_index = 0
        self.num_projects = 0

    def prepare_build_jobs(self, projects):
        # projects are received already sorted by build order
        # this means, no project can depend on projects which
        # come after it in the list!!!!
        self.num_projects = len(projects)
        for project in projects:
            job = BuildJob(project)
            self.all_jobs.append(job)
            self._resolve_job_build_dependencies(job)
            # job has dependencies => pending
            if job.deps:
                self.pending_jobs.append(job)
            # job has no dependencies => running
            else:
                self._schedule_job(job)

    def build(self, *args, **kwargs):
        num_workers = kwargs.get("num_workers", 1)
        kwargs.pop("num_workers", None)
        # start workers
        for i in range(0, num_workers):
            worker = BuildWorker(self.running_jobs, i, *args, **kwargs)
            self._workers.append(worker)
            worker.start()

        all_ok = True
        while all_ok and \
              (self.pending_jobs or not self.running_jobs.empty()):

            # parse pending_jobs to see if any needs to be moved to running
            for job in self.pending_jobs:
                if not job.deps:
                    self._schedule_job(job)
                    self.pending_jobs.remove(job)

            # check if any worker failed
            for worker in self._workers:
                if not worker.result.ok:
                    all_ok = False
                    self.failed_project = worker.result.failed_project
                    break

        # end (all done or error)
        # say to all workers to stop
        for worker in self._workers:
            worker.stop()

        # join all workers before quitting
        for worker_thread in self._workers:
            worker_thread.join()

        # compilation failed
        if not all_ok:
            raise qibuild.build.BuildFailed(self.failed_project)


    def _schedule_job(self, job):
        job.index = self.job_current_index
        self.job_current_index += 1
        job.num_projects = self.num_projects
        self.running_jobs.put(job)


    def _resolve_job_build_dependencies(self, job):
        for p in job.project.build_depends:
            dep_job = self._find_job_by_name(p)
            if dep_job:
                job.add_dependency(dep_job)
            else:
                ui.debug("Job {job}: Couldn't find the job for the project dependency {dep}". \
                    format(job=job.project.name, dep=p))

    def _find_job_by_name(self, name):
        for job in self.all_jobs:
            if (job.project.name == name):
                return job

        return None



class BuildResult(object):
    def __init__(self):
        self.ok = True
        self.failed_project = None



class BuildWorker(threading.Thread):
    def __init__(self, queue, worker_index, *args, **kwargs):
        super(BuildWorker, self).__init__(name="BuildWorker#%i" % worker_index)
        self.index = worker_index
        self.queue = queue
        self.args = args
        self.kwargs = kwargs
        self._should_stop = False
        self.result = BuildResult()

    def stop(self):
        """ Tell the worker it should stop trying to read items from the queue """
        self._should_stop = True

    def run(self):
        while not self._should_stop and self.result.ok:
            job = None
            try:
                job = self.queue.get(True, 1);
            except Queue.Empty:
                # ignore empty exception, this can happen
                pass

            if job:
                try:
                    ui.info(ui.green, "Worker #%i starts working on " % (self.index + 1), ui.reset, ui.bold, job.project.name)
                    job.execute(*self.args, **self.kwargs)
                    self.queue.task_done()
                except Exception, e:
                    self.result.ok = False
                    self.result.failed_project = job.project
                    ui.error(*self.message_for_exception(e))

    def message_for_exception(self, exception):
        tb = sys.exc_info()[2]
        io = StringIO.StringIO()
        traceback.print_tb(tb, file=io)
        return (ui.red, "Python exception during tests:\n",
                exception.__class__.__name__,
                str(exception), "\n",
                ui.reset,
                io.getvalue())
