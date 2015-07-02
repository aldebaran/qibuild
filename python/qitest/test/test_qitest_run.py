import json

import qisys.command
import qibuild.find

def test_simple_run(tmpdir, qitest_action):
    ls = qisys.command.find_program("ls")
    tests = [
            { "name": "ls", "cmd" : [ls], "timeout" : 1 }
    ]
    qitest_json = tmpdir.join("qitest.json")
    qitest_json.write(json.dumps(tests))
    qitest_action("run", cwd=tmpdir.strpath)
