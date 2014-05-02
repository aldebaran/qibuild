#include <Python.h>

static PyObject* b_b(PyObject *self, PyObject *args)
{
  printf("b\n");
  Py_RETURN_NONE;
}

static PyMethodDef b_methods[] = {
  {"b", b_b, METH_VARARGS, "print b"},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_b()
{
  (void) Py_InitModule("_b", b_methods);
}
