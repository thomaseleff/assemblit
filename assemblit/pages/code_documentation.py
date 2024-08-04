""" Page builder """

import os
import inspect
from typing import Any
import streamlit as st
from assemblit import setup
from assemblit.pages._components import _core


class Content():
    """ A `class` that contains the code documentation-page content.

    Parameters
    ----------
    package : `str`
        The package that contains `package_or_module`.
    package_or_module : `str`
        The package or module to document.

    Examples
    --------

    ``` python

    # Constructing the code documentation-page content

    from assemblit import pages

    Documentation = pages.code_documentation.Content(
        package=assemblit,
        package_or_module=pages  # Generates this documentation page
    )

    # Serving the code documentation-page content

    Documentation.serve()

    ```
    """

    def __init__(
        self,
        package: object,
        package_or_module: object,
    ):
        """ Initializes an instance of the code documentation-page content.

        Parameters
        ----------
        package : `str`
            The package that contains `package_or_module`.
        package_or_module : `str`
            The package or module to document.
        """

        # Assign content class variables
        self.package = package
        self.package_or_module = package_or_module

        # Initialize session state defaults
        _core.initialize_session_state_defaults()

    def serve(
        self
    ):
        """ Serves the code documentation-page content.
        """

        # Manage authentication
        if st.session_state[setup.NAME][setup.AUTH_NAME][setup.AUTH_QUERY_INDEX]:

            # Relative path
            relative_path = _get_relative_path(inspect.getfile(self.package_or_module), inspect.getfile(self.package))

            # Parse header
            if object_title := _parse_object_title(self.package_or_module):
                header = '%s ― %s' % (str(self.package_or_module.__name__).split('.')[-1], object_title)
            else:
                header = '%s' % (str(self.package_or_module.__name__).split('.')[-1])

            # Display header
            _core.display_page_header(
                header=header,
                tagline=_parse_object_tagline_information(relative_path=relative_path)
            )

            if _is_package(self.package_or_module):

                # Display `package` documentation
                if subpackages_or_modules := _contains_modules(self.package, self.package_or_module):

                    # Display `package` table of contents
                    self._display_package_table_of_contents(
                        obj=self.package_or_module,
                        subpackages_or_modules=subpackages_or_modules
                    )

                    # Display `module` documentation
                    for name, module in subpackages_or_modules:
                        self._display_module_documentation(module_name=name, obj=module)

                else:
                    self._display_module_documentation(obj=self.package_or_module)

            else:
                self._display_module_documentation(obj=self.package_or_module)

    # Define generic service function(s)
    def _display_package_table_of_contents(self, obj: Any, subpackages_or_modules: Any):

        # Layout columns
        _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

        # Display sub-header
        col2.markdown('## Table of contents')
        col2.markdown('The `%s` namespace contains the following public subpackages and/or modules.' % (obj.__name__))

        # Construct `package` table of contents
        package_table_of_contents = []
        for name, subpackage_or_module in subpackages_or_modules:

            # Relative path
            relative_path = _get_relative_path(inspect.getfile(subpackage_or_module), inspect.getfile(self.package))

            package_table_of_contents.append(
                _parse_object_table_of_contents_information(name=name, obj=subpackage_or_module, relative_path=relative_path)
            )

        # Display `package` table of contents
        col2.markdown(
            '<ul>%s</ul>' % (
                ''.join(package_table_of_contents)
            ),
            unsafe_allow_html=True
        )

    def _display_module_table_of_contents(
        self,
        module_name: str | None,
        obj: Any,
        classes_or_functions: Any
    ):

        # Layout columns
        _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

        # Display sub-header
        if module_name:
            if object_title := _parse_object_title(obj):
                col2.markdown('## %s ― %s' % (module_name, object_title))
            else:
                col2.markdown('## %s', module_name)
        col2.markdown('The `%s` module contains the following public classes and/or functions.' % (obj.__name__))

        # Construct `module` table of contents
        module_table_of_contents = []
        for name, obj in classes_or_functions:

            # Relative path
            relative_path = _get_relative_path(inspect.getfile(obj), inspect.getfile(self.package))

            module_table_of_contents.append(
                _parse_object_table_of_contents_information(
                    name=name,
                    obj=obj,
                    relative_path=relative_path,
                    line=_get_source_line(obj)
                )
            )

        # Display `module` table of contents
        col2.markdown(
            '<ul>%s</ul>' % (
                ''.join(module_table_of_contents)
            ),
            unsafe_allow_html=True
        )

    def _display_class_documentation(self, class_name: str, obj: Any):

        # Layout columns
        _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

        # Relative path
        relative_path = _get_relative_path(inspect.getfile(obj), inspect.getfile(self.package))

        # Display `class` documentation
        col2.markdown('### %s' % (class_name))
        col2.markdown(
            _parse_object_information(obj, relative_path),
            unsafe_allow_html=True
        )

        if doc := inspect.getdoc(obj):
            col2.code(doc, language='markdown')

    def _display_method_documentation(self, methods: Any):

        # Layout columns
        _, col2, _ = st.columns(setup.INDENTED_CONTENT_COLUMNS)

        # Display `method` documentation
        col2.markdown('#### Methods')
        for _, method in methods:

            # Relative path
            relative_path = _get_relative_path(inspect.getfile(method), inspect.getfile(self.package))

            with col2.container(border=True):
                st.markdown(
                    _parse_object_information(method, relative_path),
                    unsafe_allow_html=True
                )

                if doc := inspect.getdoc(method):
                    st.code(doc, language='markdown')

    def _display_function_documentation(self, functions: Any):

        # Layout columns
        _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

        # Display `function` documentation
        col2.markdown('#### Functions')
        for _, fn in functions:

            # Relative path
            relative_path = _get_relative_path(inspect.getfile(fn), inspect.getfile(self.package))

            with col2.container(border=True):
                st.markdown(
                    _parse_object_information(fn, relative_path),
                    unsafe_allow_html=True
                )

                if doc := inspect.getdoc(fn):
                    st.code(doc, language='markdown')

    def _display_exception_documentation(self, exceptions: Any):

        # Layout columns
        _, col2, _ = st.columns(setup.CONTENT_COLUMNS)

        # Display `exception` documentation
        col2.markdown('#### Exceptions')
        for _, exception in exceptions:

            # Relative path
            relative_path = _get_relative_path(inspect.getfile(exception), inspect.getfile(self.package))

            with col2.container(border=True):
                st.markdown(
                    _parse_object_information(exception, relative_path),
                    unsafe_allow_html=True
                )

                if doc := inspect.getdoc(exception):
                    st.code(doc, language='markdown')

    def _display_module_documentation(self, obj: Any, module_name: str | None = None):
        if classes := _contains_classes(self.package, obj):

            # Check for functions
            if functions := _contains_methods(self.package, obj):
                classes_or_functions = classes + functions
            else:
                classes_or_functions = classes

            # Display `module` table of contents
            self._display_module_table_of_contents(module_name=module_name, obj=obj, classes_or_functions=classes_or_functions)

            # Display `class` documentation
            for name, clss in classes:
                self._display_class_documentation(class_name=name, obj=clss)

                # Display class-level `method` documentation
                if methods := _contains_methods(self.package, clss):
                    self._display_method_documentation(methods=methods)

                # Display class-level `exception` documentation
                if exceptions := _contains_exceptions(self.package, clss):
                    self._display_exception_documentation(exceptions=exceptions)

            # Display `function` documentation
            if functions:
                self._display_function_documentation(functions=functions)

            # Display `exception` documentation
            if exceptions := _contains_exceptions(self.package, obj):
                self._display_exception_documentation(exceptions=exceptions)

        else:

            # Display `module` documentation
            if functions := _contains_methods(self.package, obj):

                # Display `module` table of contents
                self._display_module_table_of_contents(module_name=module_name, obj=obj, classes_or_functions=functions)

                # Display `function` documentation
                self._display_function_documentation(functions=functions)

            # Display `exception` documentation
            if exceptions := _contains_exceptions(self.package, obj):
                self._display_exception_documentation(exceptions=exceptions)


# Define inspection function(s)
def _get_relative_path(full_path, base_path) -> str:
    return os.path.relpath(
        full_path,
        os.path.abspath(
            os.path.join(
                os.path.dirname(base_path),
                os.pardir
            )
        )
    )


def _get_source_path(relative_path, line: int | None = None) -> str:
    if line:
        line = '#L%s' % (line)
    else:
        line = ''

    return '%s/blob/%s/%s%s' % (
        setup.GITHUB_REPOSITORY_URL,
        setup.GITHUB_BRANCH_NAME,
        relative_path,
        line
    )


def _get_source_line(obj: Any) -> int:
    return inspect.getsourcelines(obj)[1]


def _get_object_type(obj: Any) -> str:
    if os.path.basename(inspect.getabsfile(obj)) == '__init__.py':
        return 'subpackage'
    elif inspect.ismodule(obj):
        return 'module'
    elif inspect.isclass(obj):
        return 'class'
    elif inspect.isfunction(obj):
        return 'function'
    else:
        raise NotImplementedError


def _get_object_name(obj: Any) -> str:
    module = inspect.getmodule(obj)
    return '.'.join([module.__name__, obj.__qualname__])


def _get_signature(obj: Any) -> str:
    try:
        return inspect.signature(obj)
    except (IndexError, ValueError):
        return None


def _parse_parameter_annotation(obj: Any) -> str:
    try:
        return str(_get_signature(obj)).split(' ->')[0].strip()
    except IndexError:
        return ''


def _parse_return_annotation(obj: Any) -> str:
    try:
        return str(_get_signature(obj)).split(' ->')[1].strip().replace("'", '')
    except IndexError:
        return 'None'


def _parse_object_title(obj: Any) -> str:
    try:
        return [line for line in inspect.getdoc(obj).splitlines() if line][0]
    except (AttributeError, IndexError):
        return ''


def _parse_object_tagline_information(relative_path: str) -> str:
    return """
        <p>
            <span style="font-weight: bold;">Source code</span><!--
            --><span style="font-family: 'Source Code Pro', monospace; font-size: 14px;">:</span>
            <span style="font-family: 'Source Code Pro', monospace; font-size: 14px;">%s</span>
            <a href="%s">[source]</a>
        </p>
    """ % (
        relative_path,
        _get_source_path(relative_path)
    )


def _parse_object_table_of_contents_information(name: str, obj: Any, relative_path: str, line: int | None = None) -> str:
    return """<li>
        <span style="font-weight: bold;">%s </span><!--
        --><code>%s</code><!--
        --><span style="font-family: 'Source Code Pro', monospace; font-size: 14px;"> %s</span>
        <a href="%s">[source]</a>
    </li>""" % (
        name,
        _get_object_type(obj),
        relative_path,
        _get_source_path(relative_path, line)
    )


def _parse_object_information(obj: Any, relative_path: str) -> str:
    if not _get_signature(obj):
        return """
            <p>
                <code>%s</code><!--
                --><span style="font-weight: bold;"> %s</span>
                <a href="%s">[source]</a>
            </p>
        """ % (
            _get_object_type(obj),
            _get_object_name(obj),
            _get_source_path(
                relative_path,
                _get_source_line(obj)
            )
        )
    else:
        if inspect.isclass(obj):
            return """
                <p>
                    <code>%s</code><!--
                    --><span style="font-weight: bold;"> %s</span><!--
                    --><span style="font-family: 'Source Code Pro', monospace; font-size: 14px;">%s</span><!--
                    --><span style="font-family: 'Source Code Pro', monospace; font-size: 14px;"> -> </span><!--
                    --><code>%s</code>
                    <a href="%s">[source]</a>
                </p>
            """ % (
                _get_object_type(obj),
                _get_object_name(obj),
                _parse_parameter_annotation(obj.__init__),
                _parse_return_annotation(obj.__init__),
                _get_source_path(
                    relative_path,
                    _get_source_line(obj)
                )
            )
        elif inspect.isfunction(obj):
            return """
                <p>
                    <code>%s</code><!--
                    --><span style="font-weight: bold;"> %s</span><!--
                    --><span style="font-family: 'Source Code Pro', monospace; font-size: 14px;">%s</span><!--
                    --><span style="font-family: 'Source Code Pro', monospace; font-size: 14px;"> -> </span><!--
                    --><code>%s</code>
                    <a href="%s">[source]</a>
                </p>
            """ % (
                _get_object_type(obj),
                _get_object_name(obj),
                _parse_parameter_annotation(obj),
                _parse_return_annotation(obj),
                _get_source_path(
                    relative_path,
                    _get_source_line(obj)
                )
            )
        else:
            raise NotImplementedError


def _is_package(obj: Any) -> bool:
    """ Returns `True` when `obj` is a package. A package is any object that
    contains '__init__.py`.

    Parameters
    ----------
    obj : `Any`
        Object to inspect.
    """
    if os.path.basename(inspect.getabsfile(obj)) == '__init__.py':
        return True
    else:
        return False


def _is_in_package(package: Any, obj: Any) -> bool:
    """ Returns `True` when `obj` is in the `package` namespace.

    Parameters
    ----------
    package : `Any`
        Package object that defines the namespace.
    obj : `Any`
        Object to inspect.
    """

    base_path = os.path.abspath(os.path.dirname(inspect.getabsfile(package)))
    obj_path = os.path.abspath(inspect.getabsfile(obj))

    # Get the common-path
    try:
        return os.path.commonpath([obj_path, base_path]) == base_path
    except ValueError:
        return False


def _contains_modules(package: Any, obj: Any) -> list[tuple[str, Any]] | None:
    """ Returns all public modules of object.

    Parameters
    ----------
    obj : `Any`
        Object to inspect.
    """
    modules = inspect.getmembers(obj, inspect.ismodule)
    if modules:
        return [
            (name, module) for name, module in modules if
            not name.startswith('_')
            and _is_in_package(package=package, obj=module)
        ]
    else:
        return None


def _contains_classes(package: Any, obj: Any) -> list[tuple[str, Any]] | None:
    """ Returns all public classes of object. A class is any object that
    is not an instance or subclass of `Exception`.

    Parameters
    ----------
    obj : `Any`
        Object to inspect.
    """
    classes = inspect.getmembers(obj, inspect.isclass)
    if classes:
        return [
            (name, clss) for name, clss in classes if
            not name.startswith('_')
            and not isinstance(clss, Exception)
            and not issubclass(clss, Exception)
            and _is_in_package(package=package, obj=clss)
        ]
    else:
        return None


def _contains_methods(package: Any, obj: Any) -> list[tuple[str, Any]] | None:
    """ Returns all public methods of an object.

    Parameters
    ----------
    obj : `Any`
        Object to inspect.
    """
    methods = inspect.getmembers(obj, inspect.isfunction)
    if methods:
        return [
            (name, method) for name, method in methods if
            not name.startswith('_')
            and _is_in_package(package=package, obj=method)
        ]
    else:
        return None


def _contains_init(package: Any, obj: Any) -> list[tuple[str, Any]] | None:
    """ Returns `True` if an object has an __init__ method.

    Parameters
    ----------
    obj : `Any`
        Object to inspect.
    """
    methods = inspect.getmembers(obj, inspect.isfunction)
    if init := [
        (name, method) for name, method in methods if
            name == '__init__'
            and _is_in_package(package=package, obj=method)
    ]:
        return init
    else:
        return None


def _contains_exceptions(package: Any, obj: Any) -> list[tuple[str, Any]] | None:
    """ Returns all public exceptions of object. An exception is any object that
    is an instance or subclass of `Exception`.

    Parameters
    ----------
    obj : `Any`
        Object to inspect.
    """
    exceptions = inspect.getmembers(obj, inspect.isclass)
    if exceptions:
        return [
            (name, exception) for name, exception in exceptions if
            not name.startswith('_')
            and (
                isinstance(exception, Exception)
                or issubclass(exception, Exception)
            )
            and _is_in_package(package=package, obj=exception)
        ]
    else:
        return None
