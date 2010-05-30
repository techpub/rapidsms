#!/usr/bin/env python
# -*- coding= UTF-8 -*-

from sref_generic_states import Sref
from django_tracking.models import TrackedItem

from django.db import models


class MicroscopyResult(Sref):
    """
    Specimen sample state to be used when a specimen has been
    tested with microscopy.
    """

    RESULT_CHOICES = [('negative', u"Negative")]
    RESULT_CHOICES.extend(('%d+' % i, u"%d+" % i) for i in xrange(1, 4))
    RESULT_CHOICES.extend(('%d AFB' % i, u"%d AFB" % i) for i in xrange(1, 20))
    RESULT_CHOICES.append(('invalid', u"Invalid"))

    RESULT_CHOICES = tuple(RESULT_CHOICES)

    result = models.CharField(max_length=10, choices=RESULT_CHOICES)

    state_name = 'microscopy'
    state_type = 'result'

    class Meta:
        app_label = 'findtb'


    def get_web_form(self):

        from findtb.forms.sref_result_forms import MgitForm, LpaForm

        ti, created = TrackedItem.get_tracker_or_create(content_object=self.specimen)

        if ti.state.content_object.is_positive():
            return LpaForm

        return MgitForm


    def is_positive(self):
        return self.result != 'negative' and self.result != 'invalid'


    def get_short_message(self):
        return u"Microscopy result: %s" % self.get_result_display()


    def get_long_message(self):
        return u"Microscopy result for specimen of %(patient)s with "\
               u"tracking tag %(tag)s: %(result)s" % {
               'patient': self.specimen.patient,
               'tag': self.specimen.tracking_tag,
               'result': self.get_result_display()}



class MgitResult(Sref):
    """
    Specimen sample state to be used when a specimen has been
    used for MGIT.
    """

    RESULT_CHOICES = (
        ('positive', u"Positive"),
        ('negative', u"Negative"),
        ('invalid', u"Invalid")
    )

    result = models.CharField(max_length=10, choices=RESULT_CHOICES)

    state_name = 'mgit'
    state_type = 'result'

    class Meta:
        app_label = 'findtb'


    def get_web_form(self):

        pass


    def get_short_message(self):
       return u"Received at NTRL"


    def get_long_message(self):
        return u"Received specimen TC#%(tc_number)s, patient %(patient)s " \
                "from %(dtu)s" % \
               {'dtu': self.specimen.location, \
                'patient': self.specimen.patient, \
                'tc_number': self.specimen.tc_number}



class LpaResult(Sref):
    """
    Specimen sample state to be used when a specimen has been
    tested with LPA.
    """

    state_name = 'lpa'
    state_type = 'result'
    is_final = False

    RIF_CHOICES = (
        ('resistant', u"RIF Resistant") ,
        ('Susceptible', u"RIF Susceptible"),
        ('na', u"N/A"),
    )

    INH_CHOICES = (
        ('resistant', u"INH Resistant") ,
        ('Susceptible', u"INH Susceptible"),
        ('na', u"N/A"),
    )


    rif = models.CharField(max_length=15, choices=RIF_CHOICES)
    inh = models.CharField(max_length=15, choices=INH_CHOICES)

    class Meta:
        app_label = 'findtb'


    def get_web_form(self):
        from findtb.forms.sref_result_forms import LjForm
        return LjForm


    def get_short_message(self):
        return u"LPA results: INH %(inh)s and RIF %(rif)s." % {
               'inh': self.inh,
               'rif': self.rif}


    def get_long_message(self):
        return u"LPA results for specimen of %(patient)s with "\
               u"tracking tag %(tag)s: INH %(inh)s and RIF %(rif)s." % {
               'patient': self.specimen.patient,
               'tag': self.specimen.tracking_tag,
               'inh': self.inh,
               'rif': self.rif}



class LjResult(Sref):
    """
    Specimen sample state to be used when a specimen has been
    used for LJ.
    """

    state_name = 'lj'
    state_type = 'result'
    is_final = False

    RESULT_CHOICES = (
        ('positive', u"Positive"),
        ('negative', u"Negative"),
        ('invalid', u"Invalid")
    )

    result = models.CharField(max_length=10, choices=RESULT_CHOICES)


    class Meta:
        app_label = 'findtb'


    def get_web_form(self):
        from findtb.forms.sref_result_forms import SirezForm
        return SirezForm


    def get_short_message(self):
        return u"LJ result: %s" % self.get_result_display()


    def get_long_message(self):
        return u"LJ result for specimen of %(patient)s with "\
               u"tracking tag %(tag)s: %(result)s" % {
               'patient': self.specimen.patient,
               'tag': self.specimen.tracking_tag,
               'result': self.get_result_display()}



class SirezResult(Sref):
    """
    Specimen sample state to be used when a specimen has been
    tested with SIREZ.
    """

    state_name = 'sirez'
    state_type = 'result'
    is_final = False

    RIF_CHOICES = (
        ('resistant', u"RIF Resistant") ,
        ('susceptible', u"RIF Susceptible"),
        ('invalid', u"Invalid"),
    )

    INH_CHOICES = (
        ('resistant', u"INH Resistant") ,
        ('susceptible', u"INH Susceptible"),
        ('invalid', u"Invalid"),
    )

    STR_CHOICES = (
        ('resistant', u"STR Resistant") ,
        ('susceptible', u"STR Susceptible"),
        ('invalid', u"Invalid"),
    )

    EMB_CHOICES = (
        ('resistant', u"EMB Resistant") ,
        ('susceptible', u"EMB Susceptible"),
        ('invalid', u"Invalid"),
    )

    PZA_CHOICES = (
        ('untested', u"PZA Untested"),
        ('resistant', u"PZA Resistant"),
        ('susceptible', u"PZA Susceptible"),
        ('invalid', u"Invalid"),
    )

    rif = models.CharField(max_length=15, choices=RIF_CHOICES)
    inh = models.CharField(max_length=15, choices=INH_CHOICES)
    str = models.CharField(max_length=15, choices=STR_CHOICES)
    emb = models.CharField(max_length=15, choices=EMB_CHOICES)
    pza = models.CharField(max_length=15, choices=PZA_CHOICES)

    class Meta:
        app_label = 'findtb'


    def get_web_form(self):
        None


    def get_short_message(self):
        tests = ('rif', 'inh', 'str', 'emb', 'pza')
        results = ", ".join("%s: %s" % (test.upper(), getattr(self, test).upper()) for test in tests)
        return u"SIREZ results: %s" % results


    def get_long_message(self):
        tests = ('rif', 'inh', 'str', 'emb', 'pza')
        results = ", ".join("%s: %s" % (test.upper(), getattr(self, test).upper()) for test in tests)
        return u"SIREZ result for specimen of %(patient)s with "\
               u"tracking tag %(tag)s: %(result)s" % {
               'patient': self.specimen.patient,
               'tag': self.specimen.tracking_tag,
               'result': results}

