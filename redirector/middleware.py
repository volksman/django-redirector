from django import http
from django.conf import settings
from django.utils.timezone import now
from django.contrib.sites.shortcuts import get_current_site

from .models import Redirect, Referral
from . import settings as redirect_settings


class RedirectorMiddleware(object):
    """
    This middleware checks to see if the current request has resulted in a 404 error, and if it has
    it then checks to see if there is a redirect specified.  If there is none, it will store the url that
    generated the 404 error.

    The middleware takes the full path of the request and attempts to find an existing redirect with and without
    an ending slash.  In this way, these two urls would be treated as the same URL instead of two different URLs:
    /dir/foo/bar/
    /dir/foo/bar
    """

    def get_response_class(self, redirect):
        """
        Utility function for determining which response class to use based on the redirect_type value.
        :return: Class
        """
        if redirect.redirect_type == redirect_settings.PERMANENT_REDIRECT_VALUE:
            return http.HttpResponsePermanentRedirect
        if redirect.redirect_type == redirect_settings.TEMPORARY_REDIRECT_VALUE:
            return http.HttpResponseRedirect

        raise NotImplementedError("The 'redirect_type' has not been implemented correctly. "
                                  "The values are specified in advanced_redirects.settings")

    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        full_path = request.get_full_path()
        current_site = get_current_site(request)
        redirect = None

        # check to see if there is an existing redirect for the full path as is
        try:
            redirect = Redirect.objects.get(site=current_site,
                originating_url=full_path)
        except Redirect.DoesNotExist:
            pass

        # try adding a slash if there isn't and see if a redirect exists (may not be necessary)
        if request is None and settings.APPEND_SLASH and not \
            request.path.endswith('/'):

            try:
                redirect = Redirect.objects.get(
                    site=current_site,
                    originating_url=request.get_full_path(
                        force_append_slash=True))
            except Redirect.DoesNotExist:
                pass

        if redirect:
            # check for the referer to store a referral
            referer = request.META.get('HTTP_REFERER',
                redirect_settings.REFERER_NONE_VALUE)
            referral, created = Referral.objects.get_or_create(
                referer_url=referer, redirect=redirect)
            referral.hits += 1
            referral.last_hit = now()
            referral.save()

            # if default 404 redirect is specified, do a temporary redirect
            if redirect_settings.DEFAULT_404_REDIRECT:
                return http.HttpResponseRedirect(
                    redirect_settings.DEFAULT_404_REDIRECT)

            if redirect.redirect_to_url:
                response_class = self.get_response_class(redirect)
                return response_class(redirect.redirect_to_url)

        # show the 404 page
        return response
