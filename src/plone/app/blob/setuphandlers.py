# -*- coding: utf8 -*-

import logging

from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('plone.app.blob')

def convertNewsToBlobs(context):
    """Convert news items to blob version.

    We disable link integrity checks here, as the migration only
    removes objects to recreate them fresh, so in the end nothing is
    permanently removed.
    """
    logger.info('Started migration of news items to blobs.')
    from plone.app.blob.migrations import migrateATBlobNewsItems
    sprop = getToolByName(context, 'portal_properties').site_properties
    if sprop.hasProperty('enable_link_integrity_checks'):
        ori_enable_link_integrity_checks = sprop.getProperty('enable_link_integrity_checks')
        if ori_enable_link_integrity_checks:
            logger.info('Temporarily disabled link integrity checking')
            sprop.enable_link_integrity_checks = False
    else:
        ori_enable_link_integrity_checks = None

    output = migrateATBlobNewsItems(context)
    count = len(output.split('\n')) - 1
    logger.info('Migrated %s news items to blobs.' % count)

    if ori_enable_link_integrity_checks:
        logger.info('Restored original link integrity checking setting')
        sprop.enable_link_integrity_checks = ori_enable_link_integrity_checks


def migrateTo2(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-plone.app.blob:newsitem-replacement')
    convertNewsToBlobs(context)

