#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
# maintainer: tief

import sys

from django.utils.translation import ugettext as _

from ccdoc import Document, Table, Text, Section

from reportgen.utils import render_doc_to_file
from reportgen.PrintedReport import PrintedReport

from childcount.indicators import birth
from childcount.indicators import death
from childcount.indicators import family_planning
from childcount.indicators import pregnancy
from childcount.indicators import under_one
from childcount.indicators import nutrition
from childcount.indicators import fever
from childcount.indicators import registration
from childcount.indicators import danger_signs
from childcount.indicators import neonatal
from childcount.indicators import referral
from childcount.indicators import follow_up
from childcount.indicators import household
from childcount.indicators import bed_net_coverage
from childcount.indicators import bed_net_utilization
from childcount.indicators import bed_net_utilization_pregnancy as bednet_p
from childcount.indicators import school_attendance
from childcount.indicators import sanitation
from childcount.indicators import drinking_water

from childcount.models import Patient

class ReportDefinition(PrintedReport):
    title = _('MVIS Indicators')
    filename = 'MvisIndicators'
    formats = ['html', 'pdf', 'xls']

    _indicators = (
        (_("Vital Events"), (
            birth.Total,
            death.Neonatal,
            death.UnderOne,
            death.UnderFive,
            death.PregnancyRelated,
            death.OverFiveNotPregnancyRelated,
        )),
        (_("Reproductive and maternal health"), (
            family_planning.Using,
            family_planning.Women,
            pregnancy.AncZeroByMonthFour,
            pregnancy.MonthFour,
            pregnancy.AncFourByMonthEight,
            pregnancy.MonthEight,
            birth.DeliveredInClinic,
            birth.WithLocation,
        )),
        (_("Child nutrition"), (
            birth.WeightLow,
            birth.WeightRecorded,
            under_one.UnderSixMonthsBreastFeedingOnly,
            under_one.UnderSixMonthsBreastFeedingOnlyKnown,
            nutrition.Sam,
            nutrition.Known,
            registration.MuacEligible,
        )),
        (_("Child health - immunization/diarrhea/malaria (infants and under-5's)"), (
            under_one.UnderOneImmunizationUpToDate,
            under_one.UnderOneImmunizationUpToDateKnown,
            danger_signs.UnderFiveDiarrheaUncomplicated,
            danger_signs.UnderFiveDiarrheaUncomplicatedGivenOrs,
            danger_signs.UnderFiveDiarrheaUncomplicatedGivenZinc,
            danger_signs.UnderFiveFeverComplicated,
            danger_signs.UnderFiveFeverUncomplicated,
            danger_signs.UnderFiveFeverUncomplicatedRdt,
            danger_signs.UnderFiveFeverUncomplicatedRdtPositive,
            danger_signs.UnderFiveFeverUncomplicatedRdtPositiveGivenAntimalarial,
            danger_signs.UnderFiveFeverUncomplicatedRdtNegative,
            danger_signs.UnderFiveFeverUncomplicatedRdtNegativeGivenAntimalarial,
            danger_signs.UnderFiveFeverComplicatedReferred,
            danger_signs.UnderFiveFeverComplicatedReferredFollowUp,
        )),
        (_("Malaria (Over 5's)"), (
            fever.OverFiveRdtPositive,
            fever.OverFiveRdtNegative,
            fever.OverFiveRdt,
            fever.OverFiveRdtPositiveGivenAntimalarial,
            fever.OverFiveRdtNegativeGivenAntimalarial,
        )),
        (_("CHW performance"), (
            registration.UnderOne,
            pregnancy.Coverage,
            pregnancy.Total,
            follow_up.OnTime,
            referral.Urgent,
            household.UniqueNinetyDays,
            registration.Household,
            neonatal.WithinSevenDaysOfBirth,
        )),
        (_("Bednet coverage and utilization"), (
            bed_net_coverage.Total,
            bed_net_coverage.Covered,
            bed_net_coverage.Uncovered,
            bed_net_coverage.SleepingSites,
            bed_net_utilization.Total,
            bed_net_utilization.ChildrenUsing,
            bed_net_utilization.Children,
            bednet_p.Total,
            bednet_p.PregnantUsing,
            bednet_p.Pregnant,
        )),
       (_("School Attendance"), (
            school_attendance.Total,
            school_attendance.PrimarySchoolAged,
            school_attendance.PrimarySchoolAttending,
            school_attendance.NumberOfHouseholdsWithRecordedSchoolNotInSession,
        )),
        (_("Sanitation (+SAN)"), (
            sanitation.UniqueHousehold,
            sanitation.UsingImprovedSanitation,
            sanitation.ImprovedSanitationDontshare,
        )),
        (_("Drinking Water"), (
            drinking_water.UniqueHousehold,
            drinking_water.UsingImprovedDrinkingWater,
            drinking_water.TreatWater,
        )),
        (_("Under Five"), (
            registration.HasUnderFive,
            household.UnderFiveUnique_visit,
        )),
        (_("Neonatal"), (
            registration.HasNeonatal,
            household.NeonatalUnique_visit,
        )),
        (_("Pregnancy"), (
            registration.HasPregnancy,
            household.PregnancyUnique_visit,
        )),
        (_("Malaria"), (
            fever.UnderFiveRdt,
            fever.UnderFiveRdtPositive,
            fever.UnderFiveRdtNegative,
            fever.UnderFiveRdtPositiveGivenAntimalarial,
            fever.UnderFiveRdtNegativeGivenAntimalarial,
        )),
        (_("CHW performance"), (
            follow_up.Eligible,
        ))
    )

    def generate(self, time_period, rformat, title, filepath, data):
        doc = Document(title, landscape=True)

        self.set_progress(0)
        total = len(self._indicators)

        # Category, Descrip, Sub_Periods
        sub_periods = time_period.sub_periods()
        table = Table(3+len(sub_periods), \
            Text(_("MVIS Indicators: %s") % time_period.title))

        table.add_header_row([
                Text(_("Category")), 
                Text(_("Sub-Category")), 
                Text(_("Indicator"))] + \
            [Text(p.title) for p in time_period.sub_periods()])

        n_inds = sum([len(i[1]) for i in self._indicators])+1
        count = 0

        patients = Patient.objects.all()
        for i,category in enumerate(self._indicators):
            for ind in category[1]:
                row = []
                row.append(unicode(category[0]))
                row.append(unicode(sys.modules[ind.__module__].NAME))
                row.append(unicode(ind.short_name))

                for t in sub_periods:
                    row.append(ind(t, patients))
          
                table.add_row([Text(c) for c in row])

                self.set_progress(100.0 * count / n_inds)
                count += 1

        doc.add_element(table)

        rval = render_doc_to_file(filepath, rformat, doc)
        self.set_progress(100)

        return rval
