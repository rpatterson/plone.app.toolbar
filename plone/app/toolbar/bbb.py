from lxml import html
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import ViewletBase

from plone.app.layout.globals.interfaces import IViewView

from Products.CMFCore.utils import getToolByName


class IToolbarAlerts(IViewletManager):
    """A viewlet manager that renders alerts managed by the toolbar."""


class ToolbarViewlet(ViewletBase):

    def update(self):
        super(ToolbarViewlet, self).update()
        if IViewView.providedBy(self.__parent__):
            # Ensure this viewlet has the interface that the iterate
            # alert viewlets are registered against such that they
            # only show up on view, not on edit.
            alsoProvides(self, IViewView)

    def render(self):
        context, request = self.context, self.request
        tile = getMultiAdapter((context, request), name=u'plone.toolbar')

        tile_body = ''
        tree = html.fromstring(tile.index())
        for el in tree.body.getchildren():
            tile_body += html.tostring(el)

        resources = tile.resources()

        portal_url = getToolByName(context, 'portal_url')()
        view = context.restrictedTraverse('@@at_base_edit_view', None)
        if view is not None:
            fieldsets = view.fieldsets()
            fields = view.fields(fieldsets)
            css = context.getUniqueWidgetAttr(fields, 'helper_css')
            js = context.getUniqueWidgetAttr(fields, 'helper_js')
            resources.extend(portal_url + '/' + item for item in css + js)

        resources = ';'.join(resources)
        return (u'<div style="display:none;" ' + \
                    u'data-iframe="toolbar" ' + \
                    u'data-iframe-style="border:0;overflow:hidden;' + \
                    u'position:left:0px;position:fixed;top:0px;' + \
                    u'overflow:hidden;width:100%%;' + \
                    u'background-color:transparent;z-index:500;" ' + \
                    u'data-iframe-resources="%s">%s</div>' + \
                    u'\n<div data-iframe="toolbar-alerts" ' + \
                    u'data-iframe-style="position:fixed;' + \
                    u'top:58px;right:18px;' + \
                    u'background-color:transparent;z-index:500;" ' + \
                    u'data-iframe-resources="%s">%s</div>') % (
                        resources, tile_body, resources, self.index())


class NullViewlet(ViewletBase):
    """Simply view that renders an empty string.

    For BBB purposes, to disable certain viewlets, we register an override
    for the same name and context, specific to the ICMSUILayer layer, using
    this class to render nothing.
    """

    def render(self):
        return u""
