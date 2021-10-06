#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct {
    PyObject_HEAD
    PyObject *sequence;
} PySequenceView;

static void
PySequenceView_dealloc(PySequenceView *self)
{
    PyObject_GC_UnTrack(self);
    Py_DECREF(self->sequence);
    PyObject_GC_Del(self);
}

static PyObject *
PySequenceView_repr(PySequenceView *self)
{
    return PyUnicode_FromFormat("%s(%R)", Py_TYPE(self)->tp_name, self->sequence);
}

static int
PySequenceView_contains(PySequenceView *self, PyObject *value)
{
    return PySequence_Contains(self->sequence, value);
}

static Py_ssize_t
PySequenceView_len(PySequenceView *self)
{
    return PySequence_Length(self->sequence);
}

static PyObject *
PySequenceView_getitem_slice(PySequenceView *self, PySliceObject *key) {
    Py_ssize_t start, stop, step;
    PySequenceView *ret;
    PyObject *sequence;

    PySlice_Unpack((PyObject *)key, &start, &stop, &step);

    ret = PyObject_GC_New(PySequenceView, Py_TYPE(self));
    if (ret == NULL)
        return NULL;

    sequence = PySequence_GetSlice(self->sequence, start, stop);
    Py_INCREF(sequence);
    ret->sequence = sequence;
    PyObject_GC_Track(ret);
    return (PyObject *)ret;
}

static PyObject *
PySequenceView_getitem(PySequenceView *self, PyObject *key)
{
    if (PyIndex_Check(key)) {
        Py_ssize_t i;

        i = PyNumber_AsSsize_t(key, PyExc_IndexError);
        if (i == -1 && PyErr_Occurred()) {
            return NULL;
        }
        return PySequence_GetItem(self->sequence, i);
    }
    else if (PySlice_Check(key)) {
        return PySequenceView_getitem_slice(self, (PySliceObject *)key);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                "%s indices must be integers or slices, not %.200s",
                Py_TYPE(self)->tp_name, Py_TYPE(key)->tp_name);
        return NULL;
    }
}

static int
PySequenceView_traverse(PySequenceView *self, visitproc visit, void *arg)
{
    Py_VISIT(self->sequence);
    return 0;
}

static PyObject *
PySequenceView_richcompare(PySequenceView *self, PyObject *other, int op)
{
    return PyObject_RichCompare(self->sequence, other, op);
}

static PyObject *
PySequenceView_getiter(PySequenceView *self)
{
    return PyObject_GetIter(self->sequence);
}

static PyObject *
PySequenceView_index(PySequenceView *self, PyObject *args)
{
    PyObject *value;
    Py_ssize_t ret;

    if (!PyArg_ParseTuple(args, "O:index", &value)) {
        return NULL;
    }

    ret = PySequence_Index(self->sequence, value);
    if (ret == -1) {
        PyErr_Format(PyExc_ValueError, "%R is not in %s",
                     value, Py_TYPE(self)->tp_name);
        return NULL;
    }
    return PyLong_FromSsize_t(ret);
}

static PyObject *
PySequenceView_count(PySequenceView *self, PyObject *args)
{
    PyObject *value;
    Py_ssize_t ret;

    if (!PyArg_ParseTuple(args, "O:count", &value)) {
        return NULL;
    }

    ret = PySequence_Count(self->sequence, value);
    return PyLong_FromSsize_t(ret);
}

static PyObject *
SequenceView_new(PyTypeObject *cls, PyObject *args)
{
    PySequenceView *self;
    PyObject *sequence;

    if (!PyArg_ParseTuple(args, "O:SequenceView", &sequence)) {
        return NULL;
    }
    if (!PySequence_Check(sequence)) {
        PyErr_Format(PyExc_TypeError, "%s expected a sequence, not %s",
                     cls->tp_name, Py_TYPE(sequence)->tp_name);
        return NULL;
    }

    self = PyObject_GC_New(PySequenceView, cls);
    if (self == NULL)
        return NULL;

    Py_INCREF(sequence);
    self->sequence = sequence;
    PyObject_GC_Track(self);
    return (PyObject *)self;
}

static PyObject *
PySequenceView_copy(PySequenceView *self)
{
    PyObject *ret = (PyObject *)self;
    Py_INCREF(ret)
    return ret;
}

static PyObject *
PySequenceView_deepcopy(PySequenceView *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"memo", NULL};
    PyObject *memo;
    PyObject *ret = (PyObject *)self;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O:__deepcopy__", kwlist, &memo)) {
        return NULL;
    }
    Py_INCREF(ret)
    return ret;
}

static PyObject *
PySequenceView_reversed(PySequenceView *self)
{
    return PyObject_CallMethod(self->sequence, "__reversed__", NULL);
}

static PySequenceMethods PySequenceView_as_sequence = {
    .sq_length = (lenfunc)PySequenceView_len,
    .sq_item = (ssizeargfunc)PySequenceView_getitem,
    .sq_contains = (objobjproc)PySequenceView_contains,
};

static PyMappingMethods PySequenceView_as_mapping = {
    .mp_length = (lenfunc)PySequenceView_len,
    .mp_subscript = (binaryfunc)PySequenceView_getitem,
};

static PyMethodDef PySequenceView_methods[] = {
    {"index", (PyCFunction)PySequenceView_index,
     METH_VARARGS, NULL},
    {"count", (PyCFunction)PySequenceView_count,
     METH_VARARGS, NULL},
    {"__copy__", (PyCFunction)PySequenceView_copy,
     METH_NOARGS, NULL},
    {"__deepcopy__", (PyCFunction)PySequenceView_deepcopy,
     METH_VARARGS | METH_KEYWORDS, NULL},
    {"__reversed__", (PyCFunction)PySequenceView_reversed,
     METH_NOARGS, NULL},
     /* Python >= 3.9 */
#ifdef Py_GENERICALIASOBJECT_H
    {"__class_getitem__", (PyCFunction)Py_GenericAlias,
     METH_O | METH_CLASS, PyDoc_STR("See PEP 585")},
#endif
    {NULL, NULL, 0, NULL},
};

PyTypeObject PySequenceView_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    .tp_name = "SequenceView",
    .tp_basicsize = sizeof(PySequenceView),
    .tp_itemsize = 0,
    .tp_new = PyType_GenericNew,
    .tp_as_sequence = &PySequenceView_as_sequence,
    .tp_as_mapping = &PySequenceView_as_mapping,
    .tp_iter = (getiterfunc)PySequenceView_getiter,
    .tp_methods = PySequenceView_methods,
    .tp_richcompare = (richcmpfunc)PySequenceView_richcompare,
    .tp_traverse = PySequenceView_traverse,
    /* Python >= 3.10 */
#ifdef Py_TPFLAGS_SEQUENCE
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_SEQUENCE,
#else
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
#endif
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_repr = (reprfunc)PySequenceView_repr,
    .tp_str = (reprfunc)PySequenceView_repr,
    .tp_new = SequenceView_new,
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
    if (PyModule_AddObject(m, "SequenceView", (PyObject *) &PySequenceView_Type) < 0) {
        Py_DECREF(&PySequenceView_Type);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
