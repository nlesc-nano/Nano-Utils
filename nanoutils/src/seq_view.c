#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct {
    PyObject_HEAD
} PySequenceView;

static PyTypeObject PySequenceView_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "custom.Custom",
    .tp_basicsize = sizeof(PySequenceView),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "seq_view",
    .m_doc = NULL,
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_seq_view(void)
{
    PyObject *m;
    if (PyType_Ready(&PySequenceView_Type) < 0)
        return NULL;

    m = PyModule_Create(&module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&PySequenceView_Type);
    if (PyModule_AddObject(m, "PySequenceView", (PyObject *) &PySequenceView_Type) < 0) {
        Py_DECREF(&PySequenceView_Type);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
