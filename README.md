# UNIS-sunmoon

Create a plot for the altitudes of the Sun and the Moon in the sky.

The astronomical calculations are done using [Astropy](https://www.astropy.org/) and [astroplan](https://astroplan.readthedocs.io/en/latest/).

## Notes

In the standard Ubuntu installation, there was a weird error regarding GTK backends. There is apparently an unnecessary line in `backend_gtk3.py`. If you get this error, you can comment out the line `GLib.source_remove(seld._idle_draw_id)`
