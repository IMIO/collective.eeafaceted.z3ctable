# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.eeafaceted import z3ctable
from collective.eeafaceted.z3ctable import columns
from collective.eeafaceted.z3ctable import interfaces
from collective.eeafaceted.z3ctable import testing
from collective.eeafaceted.z3ctable.browser import views
from collective.eeafaceted.z3ctable.interfaces import ICollectiveEeafacetedZ3ctableLayer
from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from collective.eeafaceted.z3ctable.testing import NAKED_PLONE_INTEGRATION
from collective.eeafaceted.z3ctable.tests import views as test_views
from plone import api
from plone.app.testing import applyProfile
from plone.base.interfaces import IBundleRegistry
from plone.base.utils import get_installer
from plone.browserlayer.utils import registered_layers
from zope.i18n import translate

import unittest


class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.z3ctable into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if collective.eeafaceted.z3ctable is installed."""
        self.assertTrue(
            self.installer.is_product_installed("collective.eeafaceted.z3ctable")
        )

    def test_uninstall(self):
        """Test if collective.collective.eeafaceted.z3ctable is cleanly uninstalled."""
        self.installer.uninstall_product("collective.eeafaceted.z3ctable")
        self.assertFalse(
            self.installer.is_product_installed("collective.eeafaceted.z3ctable")
        )

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveZ3ctableLayer is registered."""
        from collective.eeafaceted.z3ctable.interfaces import (
            ICollectiveEeafacetedZ3ctableLayer,
        )
        from plone.browserlayer import utils

        self.assertTrue(ICollectiveEeafacetedZ3ctableLayer in utils.registered_layers())

    def test_js_registered(self):
        """The JS and the JS variables are registered as 2 bundles."""
        self.assertEqual(
            api.portal.get_registry_record(
                "plone.bundles/faceted-z3ctable.jscompilation"
            ),
            "++resource++collective.eeafaceted.z3ctable/collective.eeafaceted.z3ctable.js",
        )
        self.assertEqual(
            api.portal.get_registry_record(
                "plone.bundles/faceted-vars-z3ctable.jscompilation"
            ),
            "collective_eeafaceted_z3ctable_js_variables.js",
        )
        self.assertTrue(
            api.portal.get_registry_record("plone.bundles/faceted-z3ctable.enabled")
        )
        self.assertTrue(
            api.portal.get_registry_record(
                "plone.bundles/faceted-vars-z3ctable.enabled"
            )
        )

    def test_uninstall_browserlayer(self):
        """The browser layer is removed at uninstall."""
        self.installer.uninstall_product("collective.eeafaceted.z3ctable")
        self.assertNotIn(ICollectiveEeafacetedZ3ctableLayer, registered_layers())

    def test_uninstall_bundles(self):
        """The 2 bundles are removed at uninstall."""
        self.installer.uninstall_product("collective.eeafaceted.z3ctable")
        bundles = api.portal.get_tool("portal_registry").collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles"
        )
        self.assertNotIn("faceted-z3ctable", bundles)
        self.assertNotIn("faceted-vars-z3ctable", bundles)
        self.assertIn("faceted.view", bundles)

    def test_translations(self):
        """French translations."""
        self.assertEqual(
            translate(
                "Sort ascending",
                domain="collective.eeafaceted.z3ctable",
                target_language="fr",
            ),
            "Cliquez ici pour trier les éléments par ordre croissant",
        )
        self.assertEqual(
            translate(
                "boolean_value_True",
                domain="collective.eeafaceted.z3ctable",
                target_language="fr",
            ),
            "Oui",
        )

    def test_public_api(self):
        """Names imported by other packages (imio.dms.mail, collective.eeafaceted.dashboard, ...)."""
        for module, names in (
            (
                columns,
                (
                    "AbbrColumn",
                    "ActionsColumn",
                    "AwakeObjectMethodColumn",
                    "BaseColumn",
                    "BaseColumnHeader",
                    "BooleanColumn",
                    "BrowserViewCallColumn",
                    "CheckBoxColumn",
                    "ColorColumn",
                    "CreationDateColumn",
                    "DateColumn",
                    "DxWidgetRenderColumn",
                    "ElementNumberColumn",
                    "I18nColumn",
                    "IconsColumn",
                    "MemberIdColumn",
                    "ModificationDateColumn",
                    "PrettyLinkColumn",
                    "PrettyLinkWithAdditionalInfosColumn",
                    "RelationPrettyLinkColumn",
                    "RelationTitleColumn",
                    "TitleColumn",
                    "VocabularyColumn",
                    "get_user_fullname",
                ),
            ),
            (views, ("ExtendedCSSTable", "FacetedTableView")),
            (
                interfaces,
                (
                    "IBottomAboveNavManager",
                    "IBottomBelowNavManager",
                    "ICollectiveEeafacetedZ3ctableLayer",
                    "IFacetedColumn",
                    "IFacetedTable",
                    "ITopAboveNavManager",
                    "ITopBelowNavManager",
                ),
            ),
            (testing, ("IntegrationTestCase", "NAKED_PLONE_INTEGRATION")),
            (test_views, ("CALL_RESULT",)),
            (z3ctable, ("_",)),
        ):
            for name in names:
                self.assertTrue(
                    hasattr(module, name), "{0}.{1}".format(module.__name__, name)
                )


class TestInstallDependencies(unittest.TestCase):

    layer = NAKED_PLONE_INTEGRATION

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)

    def test_eeafacetednavigation_is_dependency_of_eeaz3ctable(self):
        """
        eea.facetednavigation should be installed when we install eeafaceted.z3ctable
        """
        self.assertTrue(
            not self.installer.is_product_installed("eea.facetednavigation")
        )
        applyProfile(self.portal, "collective.eeafaceted.z3ctable:testing")
        self.assertTrue(self.installer.is_product_installed("eea.facetednavigation"))
