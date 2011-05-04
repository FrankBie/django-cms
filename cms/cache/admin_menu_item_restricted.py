# -*- coding: utf-8 -*-
import logging as log

from django.conf import settings
from django.core.cache import cache

from menus.models import CacheKey

"""
Cache for the is_restricted Filter Tag
The is_restricted Filter is very costly
so we introduce a cache here

e.g. 200 Pages in different Trees produce a loading time
of 30 Seconds for the admin change list tree page 

"""

CMS_ADMIN_RESTRICTED_ITEM_KEY = u"%s:adm_m_is_rest:%s:"
CMS_ADMIN_MENU_CACHE_RESTRICTED_LANG = u"admr"


def get_admin_menu_item_restricted_lex_key(page_id=None):
    """
    function to assemble the cache key
    """
    return CMS_ADMIN_RESTRICTED_ITEM_KEY % (settings.CMS_CACHE_PREFIX, page_id)

def get_admin_menu_item_restricted_cache_key(page_id):
    """
    function to get the cache key 
    """
    return get_admin_menu_item_restricted_lex_key(page_id)

def get_all_admin_menu_item_restricted_cache_keys(site_id=None):
    if site_id is None:
        site_id = 1
    all_restricted_items_cache_keys =[ cache_key for cache_key in CacheKey.objects.filter(language=CMS_ADMIN_MENU_CACHE_RESTRICTED_LANG, site=site_id).values_list('key', flat=True)]
    return all_restricted_items_cache_keys     

def delete_admin_menu_item_restricted_cache_key(key, site_id=None):
    if site_id is None:
        site_id = 1
    keys = CacheKey.objects.filter(language=CMS_ADMIN_MENU_CACHE_RESTRICTED_LANG, site=site_id, key=key)
    for old_key in keys:
        old_key.delete()    

def get_admin_menu_item_restricted_cache(page_id, site_id=None):
    """
    Helper for reading values from cache
    """
    return cache.get(get_admin_menu_item_restricted_cache_key(page_id))

def set_admin_menu_item_restricted_cache(page_id, value, site_id=None):
    """
    Helper method for storing values in cache. Stores used keys so
    all of them can be cleaned when clean_permission_cache gets called.
    """
    # store this key, so we can clean it when required
    if site_id is None:
        site_id = 1
    if page_id is not None and value is not None:
        cache_key = get_admin_menu_item_restricted_cache_key(page_id)
        cache.set(cache_key, value, settings.CMS_CACHE_DURATIONS['permissions'])
        CacheKey.objects.get_or_create(key=cache_key, language=CMS_ADMIN_MENU_CACHE_RESTRICTED_LANG, site=site_id)

def clear_admin_menu_item_restricted_page_cache(page_id=None, site_id=None):
    """
    Cleans permission cache for given user.
    """
    from cms.utils.admin import get_page_children_ids
    
    lookup_key = get_admin_menu_item_restricted_cache_key(page_id)
    log.debug("clear_admin_menu_item_restricted_page_cache pid %s with key %s" % (page_id, lookup_key))
    keys_to_remove = []
    allrestricteditems_cache_keys = get_all_admin_menu_item_restricted_cache_keys(site_id)
    for key in allrestricteditems_cache_keys:
        if key.startswith(lookup_key):
            keys_to_remove.append(key)
            child_ids = get_page_children_ids(page_id)
            for child_id in child_ids:
                child_lookup_key = get_admin_menu_item_restricted_cache_key(child_id)
                if key.startswith(child_lookup_key):
                    keys_to_remove.append(key)
    #housekeeping        
    if len(keys_to_remove)>0:
        cache.delete_many(keys_to_remove)
    for del_key in keys_to_remove:
        delete_admin_menu_item_restricted_cache_key(del_key)
    

def clear_admin_menu_item_restricted_cache(site_id=None):
    """
    cleanup the cache and the stored cache keys
    """
    for cached_key in get_all_admin_menu_item_restricted_cache_keys(site_id):
        log.debug("clear_admin_menu_item_restricted_cache cache %s" %(cached_key))
        cache.delete(cached_key)
        delete_admin_menu_item_restricted_cache_key(cached_key)
