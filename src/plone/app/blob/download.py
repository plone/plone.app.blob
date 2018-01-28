# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from ZPublisher.HTTPRangeSupport import expandRanges
from ZPublisher.HTTPRangeSupport import parseRange


def handleIfModifiedSince(instance, REQUEST, RESPONSE):
    # HTTP If-Modified-Since header handling: return True if
    # we can handle this request by returning a 304 response
    header = REQUEST.get_header('If-Modified-Since', None)
    if header is not None:
        header = header.split(';')[0]
        # Some proxies seem to send invalid date strings for this
        # header. If the date string is not valid, we ignore it
        # rather than raise an error to be generally consistent
        # with common servers such as Apache (which can usually
        # understand the screwy date string as a lucky side effect
        # of the way they parse it).
        # This happens to be what RFC2616 tells us to do in the face of an
        # invalid date.
        try:
            mod_since = long(DateTime(header).timeTime())
        except Exception:
            mod_since = None
        if mod_since is not None:
            if instance._p_mtime:
                last_mod = long(instance._p_mtime)
            else:
                last_mod = 0
            if last_mod > 0 and last_mod <= mod_since:
                RESPONSE.setStatus(304)
                return True


def handleRequestRange(instance, length, REQUEST, RESPONSE):
    # check if we have a range in the request
    ranges = None
    range = REQUEST.get_header('Range', None)
    request_range = REQUEST.get_header('Request-Range', None)
    if request_range is not None:
        # Netscape 2 through 4 and MSIE 3 implement a draft version
        # Later on, we need to serve a different mime-type as well.
        range = request_range
    if_range = REQUEST.get_header('If-Range', None)
    if range is not None:
        ranges = parseRange(range)
        if if_range is not None:
            # Only send ranges if the data isn't modified, otherwise send
            # the whole object. Support both ETags and Last-Modified dates!
            if len(if_range) > 1 and if_range[:2] == 'ts':
                # ETag:
                if if_range != instance.http__etag():
                    # Modified, so send a normal response. We delete
                    # the ranges, which causes us to skip to the 200
                    # response.
                    ranges = None
            else:
                # Date
                date = if_range.split(';')[0]
                try:
                    mod_since = long(DateTime(date).timeTime())
                except Exception:
                    mod_since = None
                if mod_since is not None:
                    if instance._p_mtime:
                        last_mod = long(instance._p_mtime)
                    else:
                        last_mod = 0
                    if last_mod > mod_since:
                        # Modified, so send a normal response. We delete
                        # the ranges, which causes us to skip to the 200
                        # response.
                        ranges = None
            RESPONSE.setHeader('Accept-Ranges', 'bytes')
        if ranges and len(ranges) == 1:
            try:
                [(start, end)] = expandRanges(ranges, length)
                size = end - start
                RESPONSE.setHeader('Content-Length', size)
                RESPONSE.setHeader(
                    'Content-Range',
                    'bytes {0}-{1}/{2}'.format(start, end - 1, length))
                RESPONSE.setStatus(206)  # Partial content
                return dict(start=start, end=end)
            except ValueError:
                return {}
    return {}
