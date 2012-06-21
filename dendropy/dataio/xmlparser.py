#! /usr/bin/env python

##############################################################################
##  DendroPy Phylogenetic Computing Library.
##
##  Copyright 2010 Jeet Sukumaran and Mark T. Holder.
##  All rights reserved.
##
##  See "LICENSE.txt" for terms and conditions of usage.
##
##  If you use this work or any portion thereof in published work,
##  please cite it as:
##
##     Sukumaran, J. and M. T. Holder. 2010. DendroPy: a Python library
##     for phylogenetic computing. Bioinformatics 26: 1569-1571.
##
##############################################################################

"""
XML-parsing abstraction layer.
"""

import sys
if sys.version_info[0] >= 2 and sys.version_info[1] >= 5:
    from xml.etree import ElementTree
else:
    try:
        from elementtree import ElementTree
    except ImportError:
        try:
            from dendropy.utility import ElementTree
        except ImportError:
            sys.stderr.write("""\

    ###############################################################################
    Failed to import the XML parsing module.
    If you are trying to install DendroPy, then the installation failed because
    Python versions of less than 2.5.0 require the ElementTrees package installed.

    Please either use a newer version of Python 2 (e.g., Python 2.5, 2.6 or 2.7) to
    install DendroPy, or install the ElementTrees package from:

        http://effbot.org/zone/element.htm
        http://effbot.org/downloads/#elementtree
    ###############################################################################

    """)
            sys.exit(1)

from dendropy.utility import containers

# diagnosed_tags = []


# def diagnose_namespace(tag, namespace):
#     if tag not in diagnosed_tags:
#         diagnosed_tags.append(tag)
# #        sys.stderr.write("% 20s\t%s\n" % (tag, namespace))


# def _iter_top_children(etree, tag, namespace_list=()):
#     """
#     Returns an iterator over *top" child elements from the root
#     element that have the matching tag.
#     """
#     i = etree.findall(tag)
#     if i:
#         diagnose_namespace(tag, "no namespace decoration")
#     elif namespace_list:
#         d = {'tag' : tag}
#         for n in namespace_list:
#             d['ns'] = n
#             decorated_tag = "{%(ns)s}%(tag)s" % d
#             #print "decorated_tag = ", decorated_tag
#             i = etree.findall(decorated_tag)
#             if i:
#                 diagnose_namespace(tag, "decorated with namespace %(ns)s" % d)
#                 break
#     if not i:
#         diagnose_namespace(tag, "NOT FOUND")
#     recasting = lambda x: XmlElement(x, namespace_list=namespace_list)
#     return containers.RecastingIterator(i, recasting)


# def _getiterator(etree, tag, namespace_list=()):
#     """
#     Returns an iterator over *all* (recursively) child elements from the root
#     element that have the matching tag.
#     """
#     i = etree.getiterator(tag)
#     if i:
#         diagnose_namespace(tag, "no namespace decoration")
#     elif namespace_list:
#         d = {'tag' : tag}
#         for n in namespace_list:
#             d['ns'] = n
#             decorated_tag = "{%(ns)s}%(tag)s" % d
#             #print "decorated_tag = ", decorated_tag
#             i = etree.getiterator(decorated_tag)
#             if i:
#                 diagnose_namespace(tag, "decorated with namespace %(ns)s" % d)
#                 break
#     if not i:
#         diagnose_namespace(tag, "NOT FOUND")
#     recasting = lambda x: XmlElement(x, namespace_list=namespace_list)
#     return containers.RecastingIterator(i, recasting)


# def _invoke_method_for_namespaces(meth, tag, namespace_list=()):
#     i = meth(tag)
#     if i is not None:
#         diagnose_namespace(tag, "no namespace decoration")
#     elif namespace_list:
#         d = {'tag' : tag}
#         for n in namespace_list:
#             d['ns'] = n
#             decorated_tag = "{%(ns)s}%(tag)s" % d
#             #print "decorated_tag = ", decorated_tag
#             i = meth(decorated_tag)
#             if i is not None:
#                 diagnose_namespace(tag, "decorated with namespace %(ns)s" % d)
#                 break
#     if i is None:
#         diagnose_namespace(tag, "NOT FOUND")
#         return i
#     return _cast_to_element(i, namespace_list=namespace_list)

# def _cast_to_element(i, namespace_list=None):
#     if isinstance(i, list):
#         return [_cast_to_element(x) for x in i]
#     elif isinstance(i, str) or isinstance(i, unicode):
#         return i
#     else:
#         return XmlElement(i, namespace_list=namespace_list)

class XmlNamespaces(object):

    def __init__(self):
        self.namespace_prefix_map = {}
        self.prefix_namespace_map = {}

    def add_namespace(self, prefix, namespace):
        try:
            self.namespace_prefix_map[namespace].append(prefix)
        except KeyError:
            self.namespace_prefix_map[namespace] = [prefix]
        self.prefix_namespace_map[prefix] = namespace

class XmlObject(object):

    def __init__(self, default_namespace, element_object_type):
        self.default_namespace = default_namespace
        self._element_object_type = element_object_type

    def _get_element_object_type(self):
        if self._element_object_type is None:
            self._element_object_type = XmlElement
        return self._element_object_type
    def _set_element_object_type(self, value):
        self._element_object_type = value
    element_object_type = property(_get_element_object_type, _set_element_object_type)

    def recast_element(self, e):
        if e is None:
            return None
        return self.element_object_type(e,
                default_namespace=self.default_namespace,
                element_object_type=self.element_object_type)

    def namespaced_getiterator(self, tag):
        for element in self._element.getiterator("{%s}%s" % (self.default_namespace, tag)):
            yield self.recast_element(element)

    def namespaced_findall(self, tag):
        for element in self._element.findall("{%s}%s" % (self.default_namespace, tag)):
            yield self.recast_element(element)

    def namespaced_find(self, tag):
        return self.recast_element(self._element.find("{%s}%s" % (self.default_namespace, tag)))

    def getiterator(self, tag):
        for element in self._element.getiterator(tag):
            yield self.recast_element(element)

    def findall(self, tag):
        for element in self._element.findall(tag):
            yield self.recast_element(element)

    def find(self, tag):
        return self.recast_element(self._element.find(tag))

    def get(self, attrib_name, default=None):
        return self._element.get(attrib_name, default)

    def _get_attrib(self):
        return self._element.attrib
    attrib = property(_get_attrib)

class XmlElement(XmlObject):
    """
    Abstraction layer around an item.
    """

    def __init__(self, element, default_namespace=None, element_object_type=None):
        XmlObject.__init__(self,
                default_namespace=default_namespace,
                element_object_type=element_object_type)
        self._element = element

class XmlDocument(XmlObject):
    """
    Abstraction layer around an XML document.
    """

    def __init__(self,
            file_obj=None,
            default_namespace=None,
            element_object_type=None):
        """
        __init__ initializes a reference to the ElementTree parser, passing it
        the a file descripter object to be read and parsed or the
        ElemenTree.Element object to be used as the root element.
        """
        XmlObject.__init__(self,
                default_namespace=default_namespace,
                element_object_type=element_object_type)
        self.namespace_registry = XmlNamespaces()
        self.root = None
        if file_obj:
            self.parse_file(file_obj)

    def parse_string(self, source):
        "Loads an XML document from an XML string, source."
        raise NotImplementedError

    def parse_file(self, source):
        """
        Loads an XML document from source, which can either be a
        filepath string or a file object.
        Custom parsing to make sure namespaces are saved.
        """
        events = "start", "start-ns", "end-ns"
        root = None
        ns_map = []
        for event, elem in ElementTree.iterparse(source, events):
            if event == "start-ns":
                ns_map.append(elem)
            elif event == "start":
                if root is None:
                    root = elem
        # self.doctree = ElementTree.ElementTree(element=root)
        self.root = self.element_object_type(root)
        for prefix, namespace in ns_map:
            self.namespace_registry.add_namespace(prefix=prefix, namespace=namespace)

# class xml_document(object):
#     """
#     ElementTree requires that the complete XML be loaded in memory
#     before working with it, which may be discouraging when dealing
#     with large files. By abstracting it this way, if we want to
#     implement a more efficient approach later, we will avoid the need
#     for messing with other sections of code.
#     """

#     def __init__(self, file_obj=None, namespace_list=()):
#         """
#         __init__ initializes a reference to the ElementTree parser, passing it
#         the a file descripter object to be read and parsed or the
#         ElemenTree.Element object to be used as the root element.
#         """
#         self.namespace_list = list(namespace_list)
#         self.namespace_registry = XmlNamespaces()
#         self.parse_file(file_obj)

#     def parse_string(self, source):
#         "Loads an XML document from an XML string, source."
#         raise NotImplementedError

#     def parse_file(self, source):
#         """
#         Loads an XML document from source, which can either be a
#         filepath string or a file object.
#         """
#         events = "start", "start-ns", "end-ns"

#         root = None
#         ns_map = []

#         for event, elem in ElementTree.iterparse(source, events):
#             if event == "start-ns":
#                 ns_map.append(elem)
#             # elif event == "end-ns":
#             #     ns_map.pop()
#             elif event == "start":
#                 if root is None:
#                     root = elem
#                 # elem.set(NS_MAP, dict(ns_map))
#         # e = ElementTree.ElementTree(root)
#         # print ns_map
#         # root = ElementTree.parse(source=source)
#         self.etree = ElementTree.ElementTree(element=root)
#         for prefix, namespace in ns_map:
#             self.namespace_registry.add_namespace(prefix=prefix, namespace=namespace)

#     def iter_top_children(self, tag):
#         """
#         Returns an iterator over all top-level elements from the root element
#         that have the matching tag.
#         """
#         return _iter_top_children(self.etree.getroot(), tag, self.namespace_list)

#     def getiterator(self, tag):
#         """
#         Returns an iterator over all top-level elements from the root element
#         that have the matching tag.
#         """
#         return _getiterator(self.etree.getroot(), tag, self.namespace_list)

#     def find(self, path):
#         "Finds all matching subelements, by tag name or path."
#         return _invoke_method_for_namespaces(self.etree.find, path, self.namespace_list)

#     def findall(self, path):
#         "Finds all matching subelements, by tag name or path."
#         return _invoke_method_for_namespaces(self.etree.findall, path, self.namespace_list)

# # class XmlElement(object):
# #     """
# #     Generic XML element. May contain child elements. At present a
# #     simple wrapper around the ElementTree.Element class, and
# #     implementing just the components of the ElementTree.Element
# #     interface that are needed for DendroPy.
# #     """

# #     def __init__(self, element, namespace_list=()):
# #         """
# #         __init__ initializes a basic structure of object. `element` is an
# #         ElementTree.Element object.
# #         """
# #         self.namespace_list = namespace_list
# #         self.etree_element = element

# #     def iter_top_children(self, tag):
# #         "Returns an iterator over child elements with tags that match `tag`."
# #         return _iter_top_children(self.etree_element, tag, self.namespace_list)

# #     def getiterator(self, tag):
# #         "Returns an iterator over child elements with tags that match `tag`."
# #         return _getiterator(self.etree_element, tag, self.namespace_list)

# #     def get(self, key, default=None):
# #         """
# #         Returns the attribute of this element with matching key, or
# #         substituting default if not found.
# #         """
# #         i = _invoke_method_for_namespaces(self.etree_element.get, key, self.namespace_list)
# #         if not i:
# #             return default
# #         return i

# #     def findtext(self, text):
# #         "Finds free text contained in element"
# #         return _invoke_method_for_namespaces(self.etree_element.findtext, text, self.namespace_list)

# #     def find(self, path):
# #         "Finds all matching subelements, by tag name or path."
# #         return _invoke_method_for_namespaces(self.etree_element.find, path, self.namespace_list)

# #     def findall(self, path):
# #         "Finds all matching subelements, by tag name or path."
# #         return _invoke_method_for_namespaces(self.etree_element.findall, path, self.namespace_list)

# #     def __getattr__(self, name):
# #         if name == 'attrib':
# #             return self.etree_element.attrib
# #         raise AttributeError(name)
