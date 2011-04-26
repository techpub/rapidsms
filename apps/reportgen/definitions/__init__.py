#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8

__all__ = ('Utilization','BednetCoverage',\
            'CHWList')

# This is the way we get the celery workers
# to register all of the ReportDefinition tasks
from reportgen.definitions import *
