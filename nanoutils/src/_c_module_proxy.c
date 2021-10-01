#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct {
    PyObject_HEAD
    PyObject *m_self;
    PyObject *m_module;
} PyModuleProxy;

static PyObject *
PyModuleProxy_richcompare(PyObject *self, PyObject *other, int op)
{
    PyModuleProxy *a, *b;
    PyObject *res;
    int eq;

    if (op != Py_EQ && op != Py_NE) || (PyObject_Type(self) != PyObject_Type(other)) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    a = (PyModuleProxy *)self;
    b = (PyModuleProxy *)other;
    eq = a->m_self == b->m_self;
    if (op == Py_EQ)
        res = eq ? Py_True : Py_False;
    else
        res = eq ? Py_False : Py_True;
    Py_INCREF(res);
    return res;
}

static PyObject *
PyModuleProxy_repr(ModuleProxy *self)
{
    PyTypeObject *m_cls = Py_TYPE(self->m_self)
    return PyUnicode_FromFormat("<%s wrapper of %s object>",
                                PyModule_GetName(self->m_module),
                                Py_TYPE(self->m_self)->tp_name);
}

static PyObject *
PyModuleProxy_hash(ModuleProxy *self)
{
    return PyLong_FromVoidPtr(self->m_self);
}

static PyObject *
PyModuleProxy_new(ModuleProxy *self, PyObject *args)
{
    PyObject *obj = NULL;
    ModuleProxy *ret;

    if (!PyArg_ParseTuple(args, "O", &arg)) {
        return NULL;
    }

    ModuleProxy *ret = PyObject_GC_New(ModuleProxy, &PyModuleProxy_Type);
    if (ret == NULL) {
        return NULL;
    }
    ret->m_self = obj;
    ret->m_module = NULL;
    Py_INCREF(obj);
    return (PyObject *)ret

}

static PyMethodDef PyModuleProxy_Methods[] = {
#ifdef Py_GENERICALIASOBJECT_H
    {"__class_getitem__", (PyCFunction)Py_GenericAlias,
            METH_O | METH_CLASS, PyDoc_STR("See PEP 585")},
#endif
    {NULL, NULL, NULL, NULL},
};

PyTypeObject PyModuleProxy_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    .tp_name = "ModuleProxyBase",
    .tp_basicsize = sizeof(ModuleProxy),
    .tp_methods = PyModuleProxy_Methods,
    .tp_richcompare = (richcmpfunc)PyModuleProxy_richcompare,
    .tp_traverse = PySequenceView_traverse,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_repr = (reprfunc)PyModuleProxy_repr,
    .tp_new = PyModuleProxy_new,
    .tp_hash = (hashfunc)PyModuleProxy_hash,
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_c_module_proxy",
    .m_doc = NULL,
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_module(void)
{
    PyObject *m;
    if (PyType_Ready(&PySequenceView_Type) < 0)
        return NULL;

    m = PyModule_Create(&module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&PySequenceView_Type);
    if (PyModule_AddObject(m, "ModuleProxyBase", (PyObject *) &PyModuleProxy_Type) < 0) {
        Py_DECREF(&PyModuleProxy_Type);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
