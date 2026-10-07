# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.subtypes.interfaces import IPossibleFacetedNavigable
from plone import api
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

# from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from plone.testing import z2
from plone.testing import zope
from Products.CMFPlone.utils import getFSVersionTuple
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import getMultiAdapter
from zope.globalrequest.local import setLocal
from zope.interface import alsoProvides

import collective.eeafaceted.z3ctable
import unittest


IS_PLONE_6 = getFSVersionTuple()[0] >= 6
# decorates a test pinning a Plone 4 behaviour that is broken on Plone 6
plone6_regression = unittest.expectedFailure if IS_PLONE_6 else (lambda f: f)


class ITestingType(model.Schema):

    afield = schema.TextLine(title="A field", required=False)

    bool_field = schema.Bool(title="Boolean field", required=False, default=True)

    rel_item = RelationChoice(
        title="Rel item",
        vocabulary="plone.app.vocabularies.Catalog",
        required=False,
    )

    rel_items = RelationList(
        title="Related Items",
        default=[],
        value_type=RelationChoice(
            title="Related", vocabulary="plone.app.vocabularies.Catalog"
        ),
        required=False,
    )


class ITestingTypeWithFieldset(ITestingType):

    model.fieldset("extra", label="Extra", fields=["extra_field"])
    extra_field = schema.TextLine(title="Extra field", required=False)


class NakedPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    products = ("collective.eeafaceted.z3ctable", "eea.facetednavigation")

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.eeafaceted.z3ctable, name="testing.zcml")
        for p in self.products:
            z2.installProduct(app, p)

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, "collective.eeafaceted.z3ctable")


NAKED_PLONE_FIXTURE = NakedPloneLayer(name="NAKED_PLONE_FIXTURE")

NAKED_PLONE_INTEGRATION = IntegrationTesting(
    bases=(NAKED_PLONE_FIXTURE,), name="NAKED_PLONE_INTEGRATION"
)


class CollectiveEeafacetedZ3ctableLayer(NakedPloneLayer):

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        setLocal("request", portal.REQUEST)
        # Install into Plone site using portal_setup
        applyProfile(portal, "collective.eeafaceted.z3ctable:testing")

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        # make sure we have a default workflow
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        eea_folder = api.content.create(
            type="Folder", id="eea_folder", title="EEA Folder", container=portal
        )
        eea_folder.reindexObject()

        alsoProvides(eea_folder, IPossibleFacetedNavigable)
        subtyper = getMultiAdapter(
            (eea_folder, eea_folder.REQUEST), name="faceted_subtyper"
        )
        subtyper.enable()

        IFacetedLayout(eea_folder).update_layout("faceted-table-items")

        # Commit so that the test browser sees these objects
        import transaction

        transaction.commit()


FIXTURE = CollectiveEeafacetedZ3ctableLayer(name="FIXTURE")


INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="INTEGRATION")


FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="FUNCTIONAL")


class AcceptanceTesting(FunctionalTesting):
    """Robot layer (MIGRATION.md Known issues):
    - the "Portal type" criterion goes on top: on the right, it covers the right part of the wide table;
    - eea.facetednavigation 16 loads its bundles async: faceted.view may run before faceted.jquery
      (jQuery.bbq undefined, results never loaded). Load them in document order."""

    def testSetUp(self):
        super(AcceptanceTesting, self).testSetUp()
        ICriteria(self["portal"]["eea_folder"]).edit("c1", position="top")
        registry = self["portal"].portal_registry
        for bundle in ("faceted.jquery", "faceted.view", "faceted.edit"):
            registry["plone.bundles/{0}.load_async".format(bundle)] = False
        import transaction

        transaction.commit()


ACCEPTANCE = AcceptanceTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="ACCEPTANCE",
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.maxDiff = None
        self.portal = self.layer["portal"]
        self.eea_folder = self.portal.get("eea_folder")
        self.faceted_z3ctable_view = self.eea_folder.restrictedTraverse(
            "faceted-table-view"
        )


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
