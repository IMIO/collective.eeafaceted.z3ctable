# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.browser.widgets import SortingFormAwareAbstractWidget
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import BrowserViewCallColumn
from collective.eeafaceted.z3ctable.interfaces import IBottomAboveNavManager
from collective.eeafaceted.z3ctable.interfaces import IBottomBelowNavManager
from collective.eeafaceted.z3ctable.interfaces import ITopAboveNavManager
from collective.eeafaceted.z3ctable.interfaces import ITopBelowNavManager
from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from collective.eeafaceted.z3ctable.testing import plone6_regression
from eea.facetednavigation.interfaces import ICriteria
from plone import api
from plone.batching import Batch
from zope.component import queryMultiAdapter
from zope.testing.loggingsupport import InstalledHandler
from zope.viewlet.interfaces import IViewletManager

import lxml.etree
import lxml.html


class TestTable(IntegrationTestCase):

    def test_Table_sortingCriterionName(self):
        """Test the _sortingCriterionName method that returns the __name__
           of the faceted 'sorting' criterion."""
        table = self.faceted_z3ctable_view
        # it is initialized together with the table and stored in table.sorting_criterion_name
        self.assertEqual(table._sortingCriterionName(), u'c2')
        self.assertEqual(table._sortingCriterionName(), table.sorting_criterion_name)
        # and it is actually the faceted sorting criterion
        self.assertEqual(ICriteria(table.context).get('c2').widget, u'sorting')
        # remove this widget, when no 'sorting' criterion found, entire sorting ability is disabled
        ICriteria(table.context).delete('c2')
        self.assertEqual(table._sortingCriterionName(), None)

    def test_Table_render_table(self):
        """Test the renderRow method that makes it possible for a single column
           to set CSS on the rendered row."""
        table = self.faceted_z3ctable_view
        # build a Batch and render the table
        brains = self.portal.portal_catalog(portal_type='Folder')
        # 1 brain
        self.assertEqual(len(brains), 1)
        batch = Batch(brains, size=5)
        rendered_table = lxml.html.fromstring(table.render_table(batch))
        # we have one table with 7 columns and 1 row
        rows = rendered_table.xpath('//table//tbody/tr')
        # 1 row
        self.assertEqual(len(rows), 1)
        columns = rendered_table.xpath('//table//thead/tr/th')
        # 9 columns
        self.assertEqual(len(columns), 9)
        # the brain is actually displayed in the table
        brain = brains[0]
        cell = rendered_table.xpath('//table//tbody/tr/td')[0]
        self.assertEqual(cell.text_content(), brain.Title)

    def test_Table_CSS_on_tr_from_cell(self):
        """table.renderRow was overrided to take into account 'tr' CSS classes defined on a column."""
        table = self.faceted_z3ctable_view
        column = BaseColumn(self.portal, self.portal.REQUEST, table)
        column.attrName = 'Title'
        table.nameColumn(column, 'Title')
        # build a Batch
        brains = self.portal.portal_catalog(portal_type='Folder')
        batch = Batch(brains, size=5)
        # adapt css defined for column to change <tr> applied CSS
        column.getCSSClasses = lambda x: {'tr': 'special_tr_class'}
        # ok, now make table.setUpColumns take our configured column
        self.portal.REQUEST.set('column', column)
        table.setUpColumns = lambda *x: [__import__('zope').component.hooks.getSite().REQUEST.get('column'), ]
        rendered_table = lxml.html.fromstring(table.render_table(batch))
        # the class is applied to the <tr>, in addition to the 'odd' class
        self.assertEqual(rendered_table.find('tbody').find('tr').attrib['class'], 'odd special_tr_class')

    def test_columns_ordering(self):
        """table.orderColumns take the ignoreColumnWeight parameter into account
        to keep columns as ordered by setUpColumns or to order them by weight."""
        table = self.faceted_z3ctable_view

        # when ignoreColumnWeight is set to True, colums are kept ordered
        # as found on setUpColumns
        table.ignoreColumnWeight = True
        table.initColumns()

        columns = [col.__name__ for col in table.columns]
        self.assertEqual(columns, table._getViewFields())

        weights = [col.__class__.weight for col in table.columns]
        ordered_weights = sorted(weights)
        self.assertNotEqual(weights, ordered_weights)

        # when ignoreColumnWeight is set to False, colums are kept ordered
        # by weight on each column
        table.ignoreColumnWeight = False
        table.initColumns()

        columns = [col.__name__ for col in table.columns]
        self.assertNotEqual(columns, table._getViewFields())

        weights = [col.__class__.weight for col in table.columns]
        ordered_weights = sorted(weights)
        self.assertEqual(weights, ordered_weights)

    def test_Table_render_table_error(self):
        """When the table can not be rendered, a message is returned and the error is logged."""
        table = self.faceted_z3ctable_view
        # a misconfigured column: no view_name
        column = BrowserViewCallColumn(self.portal, self.portal.REQUEST, table)
        table.setUpColumns = lambda: [table.nameColumn(column, 'broken')]
        brains = self.portal.portal_catalog(portal_type='Folder')
        handler = InstalledHandler('collective.eeafaceted.z3ctable')
        try:
            rendered = table.render_table(Batch(brains, size=5))
        finally:
            handler.uninstall()
        self.assertTrue(rendered.startswith('An error occured'))
        self.assertTrue(rendered.endswith('this should not happen, try to go back to the home page.'))
        self.assertEqual([record.levelname for record in handler.records], ['ERROR'])

    @plone6_regression
    def test_Table_listing_css_class(self):
        """The table has the Plone 'listing' CSS class, other packages' CSS rely on it."""
        table = self.faceted_z3ctable_view
        brains = self.portal.portal_catalog(portal_type='Folder')
        rendered_table = lxml.html.fromstring(table.render_table(Batch(brains, size=5)))
        css_classes = rendered_table.xpath('//table')[0].get('class').split()
        self.assertIn('faceted-table-results', css_classes)
        self.assertIn('listing', css_classes)


class TestFacetedTableItems(IntegrationTestCase):

    def test_faceted_table_items(self):
        """The 'faceted-table-items' layout of the faceted folder, as loaded by the faceted JS."""
        request = self.portal.REQUEST
        # no Document
        request.form['c1[]'] = 'Document'
        page = lxml.html.fromstring(self.eea_folder.restrictedTraverse('@@faceted_query')())
        self.assertEqual(page.xpath('//span[@class="table_faceted_no_results"]')[0].text, 'No results were found.')
        self.assertEqual(page.xpath('//strong[@id="search-results-number"]'), [])
        self.assertEqual(page.xpath('//table'), [])
        # 2 results
        api.content.create(container=self.eea_folder, type='testingtype', title='My testing type 1')
        api.content.create(container=self.eea_folder, type='testingtype', title='My testing type 2')
        request.form['c1[]'] = 'testingtype'
        page = lxml.html.fromstring(self.eea_folder.restrictedTraverse('@@faceted_query')())
        self.assertEqual(page.xpath('//span[@class="table_faceted_no_results"]'), [])
        count = page.xpath('//strong[@id="search-results-number"]')[0]
        self.assertEqual(' '.join(count.getparent().text_content().split()), '2 items matching your search terms.')
        self.assertEqual(len(page.xpath('//table[@id="faceted_table"]/tbody/tr')), 2)
        # refresh link
        refresh = page.xpath('//div[@class="table_faceted_results"]/a')[0]
        self.assertIn('Faceted.URLHandler.hash_changed()', refresh.get('onclick'))
        self.assertTrue(refresh.find('img').get('src').endswith('/++resource++collective.eeafaceted.z3ctable/refresh.gif'))
        # Plone 4 translates the msgid in English, Plone 6 does not (macro used without its i18n:domain)
        self.assertIn(refresh.text_content().strip(), ('Refresh search', 'Refresh search results.'))
        # 4 viewlet managers around the batch navigation
        for div_id, name, iface in (
                ('viewlet-top-above-nav', 'topabovenav', ITopAboveNavManager),
                ('viewlet-top-below-nav', 'topbelownav', ITopBelowNavManager),
                ('viewlet-bottom-above-nav', 'bottomabovenav', IBottomAboveNavManager),
                ('viewlet-bottom-below-nav', 'bottombelownav', IBottomBelowNavManager)):
            self.assertEqual(len(page.xpath('//div[@id="{0}"]'.format(div_id))), 1)
            manager = queryMultiAdapter((self.eea_folder, request, self.faceted_z3ctable_view), IViewletManager,
                                        name='collective.eeafaceted.z3ctable.' + name)
            self.assertTrue(iface.providedBy(manager))


class TestSortingFormAwareAbstractWidget(IntegrationTestCase):

    def test_query(self):
        """The hidden sorting criterion uses the sorting given in the form (column headers)."""
        criteria = ICriteria(self.eea_folder)
        widget_class = criteria.widget(cid='c2')
        # it replaces eea.facetednavigation's sorting widget
        self.assertIs(widget_class, SortingFormAwareAbstractWidget)
        request = self.portal.REQUEST
        widget = widget_class(self.eea_folder, request, criteria.get('c2'))
        self.assertTrue(widget.hidden)
        # nothing in the form: default sorting, stored in the request form
        self.assertEqual(widget.query({}), {'sort_on': 'effective', 'sort_order': 'descending'})
        self.assertEqual(request.form['c2[]'], 'effective')
        self.assertTrue(request.form['reversed'])
        # sorting given in the form
        self.assertEqual(widget.query({'c2': 'sortable_title'}),
                         {'sort_on': 'sortable_title', 'sort_order': 'ascending'})
        self.assertEqual(widget.query({'c2': 'sortable_title', 'reversed': 'on'}),
                         {'sort_on': 'sortable_title', 'sort_order': 'descending'})


class TestDefaultCollectionWidgets(IntegrationTestCase):

    def test_default_collection_widgets(self):
        """Faceted criteria XML: sorting and 10 results per page."""
        xml = self.eea_folder.restrictedTraverse('@@default_collection_widgets.xml')()
        criteria = lxml.etree.fromstring(xml).findall('criteria/criterion')
        self.assertEqual(
            [(c.get('name'), c.find('property[@name="widget"]').text) for c in criteria],
            [('c0', 'sorting'), ('c1', 'resultsperpage')])
        self.assertEqual(criteria[1].find('property[@name="default"]').text, '10')


class TestJSVariables(IntegrationTestCase):

    def test_JSVariables(self):
        """JS translations, served as javascript."""
        view = self.portal.restrictedTraverse('collective_eeafaceted_z3ctable_js_variables.js')
        self.assertEqual(view(), 'var no_selected_items = "Please select at least one element.";\n')
        self.assertTrue(self.portal.REQUEST.response.getHeader('content-type').startswith('text/javascript'))
