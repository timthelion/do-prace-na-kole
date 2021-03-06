# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 18:03
from __future__ import unicode_literals

from django.db import migrations

def delete_new_trips(apps, schema_editor):
    Trip  = apps.get_model("dpnk", "Trip")
    Trip.objects.filter(direction__isnull=False).delete()

def make_new_trips(apps, schema_editor):
    Trip  = apps.get_model("dpnk", "Trip")
    GpxFile = apps.get_model("dpnk", "GpxFile")
    trips = Trip.objects.filter(direction__isnull=True)
    print(trips.count())
    trip_count = 0
    for trip in trips:
        trip_count += 1
        if trip_count % 1000 == 0:
            print(trip_count, end="\r")
        if trip.is_working_ride_to:
            if trip.trip_to:
                commute_mode = 'bicycle'
            else:
                commute_mode = 'by_other_vehicle'
        else:
            if trip.trip_to:
                commute_mode = 'bicycle'
            else:
                commute_mode = 'no_work'

        trip_to = Trip(
            direction='trip_to',
            distance=trip.distance_to,
            date=trip.date,
            commute_mode=commute_mode,
            user_attendance=trip.user_attendance,
        )
        trip_to.save()
        try:
            gpxfile_to = GpxFile.objects.get(trip=trip, direction='trip_to')
            gpxfile_to.trip = trip_to
            gpxfile_to.save()
        except GpxFile.DoesNotExist:
            pass

        if trip.is_working_ride_from:
            if trip.trip_from:
                commute_mode = 'bicycle'
            else:
                commute_mode = 'by_other_vehicle'
        else:
            if trip.trip_from:
                commute_mode = 'bicycle'
            else:
                commute_mode = 'no_work'

        trip_from = Trip(
            direction='trip_from',
            distance=trip.distance_from,
            date=trip.date,
            commute_mode=commute_mode,
            user_attendance=trip.user_attendance,
        )
        trip_from.save()
        try:
            gpxfile_from = GpxFile.objects.get(trip=trip, direction='trip_from')
            gpxfile_from.trip = trip_from
            gpxfile_from.save()
        except GpxFile.DoesNotExist:
            pass
    Trip.objects.filter(direction__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0008_auto_20160224_1802'),
    ]

    operations = [
        migrations.RunPython(make_new_trips, reverse_code=delete_new_trips),
    ]
