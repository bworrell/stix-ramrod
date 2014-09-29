from distutils.version import StrictVersion
from ramrod import (_BaseUpdater, UnknownVersionError, InvalidVersionError,
    UpdateError)

TAG_CYBOX_MAJOR  = "cybox_major_version"
TAG_CYBOX_MINOR  = "cybox_minor_version"
TAG_CYBOX_UPDATE = "cybox_update_version"

CYBOX_VERSIONS = ('2.0', '2.0.1', '2.1')


class _CyboxUpdater(_BaseUpdater):
    """Base class for CybOX updating code. Sets default values for
    CybOX-specific xpaths and namespaces.

    """
    DEFAULT_VOCAB_NAMESPACE = 'http://cybox.mitre.org/default_vocabularies-1'
    XPATH_VERSIONED_NODES = "//cybox:Observables"
    XPATH_ROOT_NODES = "//cybox:Observables"
    XPATH_OBJECT_PROPS = "//cybox:Object/cybox:Properties"

    def __init__(self):
        super(_CyboxUpdater, self).__init__()
        self.cleaned_fields = ()


    @classmethod
    def get_version(cls, observables):
        """Returns the version of the `observables` Observables node.

        This generates a version string from the ``cybox_major``,
        ``cybox_minor`` and ``cybox_update`` attribute values.

        Raises:
            UnknownVersionError: If `observables` does not contain a
                ``cybox_major_version``, ``cybox_minor_version``, or
                 ``cybox_update_version`` attribute..
        """
        cybox_major  = observables.attrib.get(TAG_CYBOX_MAJOR)
        cybox_minor  = observables.attrib.get(TAG_CYBOX_MINOR)
        cybox_update = observables.attrib.get(TAG_CYBOX_UPDATE)

        if not any((cybox_major, cybox_minor, cybox_update)):
            raise UnknownVersionError()

        if cybox_update:
            version = "%s.%s.%s" % (cybox_major, cybox_minor, cybox_update)
        else:
            version = "%s.%s" % (cybox_major, cybox_minor)

        return version


    def _check_version(self, root):
        """Checks the versions of the Observables instances found in the
        `root` document. This overrides the ``_BaseUpdater._check_version()``
        method.

        Note:
            The ``version`` attribute of `root` is compared against the
            ``VERSION`` class-level attribute.

        Args:
            root: The root node for the document.

        Raises:
            UnknownVersionError: If `root` does not contain a ``version``
                attribute.
            InvalidVersionError: If the ``version`` attribute value for `root`
                does not match the value of ``VERSION``.

        """
        roots = self._get_root_nodes(root)
        expected = self.VERSION

        for node in roots:
            found = self.get_version(node)

            if StrictVersion(expected) != StrictVersion(found):
                raise InvalidVersionError(node, expected, found)


    def update(self, root, force=False):
        """Attempts to update the `root` node. The update logic is defined
        by implementations of this class.

        Returns:
            An updated ``etree._Element`` version of `root`.

        Raises:
            UpdateError: If untranslatable fields or non-unique IDs are
                discovered in `root` and `force` is ``False``.
            UnknownVersionError: If the `root` node contains no version
                information.
            InvalidVersionError: If the `root` node contains invalid version
                information (e.g., the class expects v1.0 content and the
                `root` node contains v1.1 content).

        """
        try:
            self.check_update(root)
            updated = self._update(root)
        except (UpdateError, UnknownVersionError, InvalidVersionError):
            if force:
                self.clean(root)
                updated = self._update(root)
            else:
                raise

        return updated


from .cybox_2_0 import Cybox_2_0_Updater
from .cybox_2_0_1 import Cybox_2_0_1_Updater

CYBOX_UPDATERS = {
    '2.0': Cybox_2_0_Updater,
    '2.0.1': Cybox_2_0_1_Updater
}