#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    PyObject *sequence;
} PySequenceView;

static void
PySequenceView_dealloc(PySequenceView *pp)
{
    PyObject_GC_UnTrack(pp);
    Py_DECREF(pp->sequence);
    PyObject_GC_Del(pp);
}

static PyObject *
PySequenceView_repr(PySequenceView *pp)
{
    return PyUnicode_FromFormat("%s(%R)", Py_TYPE(pp)->tp_name, pp->sequence);
}

static int
PySequenceView_contains(PySequenceView *pp, PyObject *value)
{
    return PySequence_Contains(pp->sequence, value);
}

static Py_ssize_t
PySequenceView_len(PySequenceView *pp)
{
    return PySequence_Length(pp->sequence);
}

static PyObject *
PySequenceView_getitem(PySequenceView *pp, Py_ssize_t key)
{
    return PySequence_GetItem(pp->sequence, key);
}

static int
PySequenceView_traverse(PyObject *self, visitproc visit, void *arg)
{
    PySequenceView *pp = (PySequenceView *)self;
    Py_VISIT(pp->sequence);
    return 0;
}

static PyObject *
PySequenceView_richcompare(PySequenceView *v, PyObject *w, int op)
{
    return PyObject_RichCompare(v->sequence, w, op);
}

static PyObject *
PySequenceView_getiter(PySequenceView *pp)
{
    return PyObject_GetIter(pp->sequence);
}

static PyObject *
PySequenceView_index(PySequenceView *pp, PyObject *args)
{
    PyObject *index_name = PyUnicode_FromString("index");
    return PyObject_CallMethodObjArgs(pp->sequence, index_name, args);
}

static PyObject *
PySequenceView_count(PySequenceView *pp, PyObject *args)
{
    PyObject *count_name = PyUnicode_FromString("count");
    return PyObject_CallMethodObjArgs(pp->sequence, count_name, args);
}

static int
SequenceView_check_sequence(PyTypeObject *type, PyObject *sequence)
{
    if (!PySequence_Check(sequence)) {
        PyErr_Format(PyExc_TypeError,
                    "%R expected a sequence, not %R",
                    type->tp_name,
                    Py_TYPE(sequence)->tp_name);
        return -1;
    }
    return 0;
}

static PyObject *
SequenceView_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PySequenceView *self;
    PyObject *sequence;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", NULL, &sequence)) {
        return NULL;
    }
    if (SequenceView_check_sequence(type, sequence) == -1)
        return NULL;

    self = PyObject_GC_New(PySequenceView, type);
    if (self == NULL)
        return NULL;

    Py_INCREF(sequence);
    self->sequence = sequence;
    PyObject_GC_Track(self);
    return (PyObject *)self;
}

static PySequenceMethods PySequenceView_as_sequence = {
    (lenfunc)PySequenceView_len,                /* sq_length */
    0,                                          /* sq_concat */
    0,                                          /* sq_repeat */
    (ssizeargfunc)PySequenceView_getitem,       /* sq_item */
    0,                                          /* sq_slice */
    0,                                          /* sq_ass_item */
    0,                                          /* sq_ass_slice */
    (objobjproc)PySequenceView_contains,        /* sq_contains */
    0,                                          /* sq_inplace_concat */
    0,                                          /* sq_inplace_repeat */
};

static PyMappingMethods PySequenceView_as_mapping = {
    (lenfunc)PySequenceView_len,
    (binaryfunc)PySequenceView_getitem,
    0,
};

static PyMethodDef PySequenceView_methods[] = {
    {"index", (PyCFunction)PySequenceView_index,
     METH_VARARGS, NULL},
    {"count", (PyCFunction)PySequenceView_count,
     METH_VARARGS, NULL},
    {0}
};

static PyTypeObject PySequenceView_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "SequenceView",                             /* tp_name */
    sizeof(PySequenceView),                     /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)PySequenceView_dealloc,         /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    (reprfunc)PySequenceView_repr,              /* tp_repr */
    0,                                          /* tp_as_number */
    &PySequenceView_as_sequence,                /* tp_as_sequence */
    &PySequenceView_as_mapping,                 /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    (reprfunc)PySequenceView_repr,              /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    PySequenceView_traverse,                    /* tp_traverse */
    0,                                          /* tp_clear */
    (richcmpfunc)PySequenceView_richcompare,    /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    (getiterfunc)PySequenceView_getiter,        /* tp_iter */
    0,                                          /* tp_iternext */
    PySequenceView_methods,                     /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    SequenceView_new,                           /* tp_new */
};

static PyMethodDef module_methods[] = {
    {"PySequenceView", &PySequenceView_Type, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "seq_view",
    NULL,
    -1,
    module_methods,
};

PyMODINIT_FUNC PyInit_seq_view(void)
{
    return PyModule_Create(&module);
}
