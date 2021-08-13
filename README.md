# NAJORK

Womble, muck and sneedball inspired musical scores.

![image](https://user-images.githubusercontent.com/778856/125062656-8bd33600-e0a6-11eb-8fa9-47292c8074ca.png)

Najork is a geometric, kinetic composition environment for music, and anything else that can consume OSC events.

It takes its inspiration from the veritable [Iannix](https://www.iannix.org/) with a focus on periodic events and modulations linked to articulated constructions.

By parenting mechanisms and objects to each other all sorts of interesting relationships can be translated in music (listener enjoyment not guaranteed).

## Project status

  - Models [80%]
  - Read file [50%]
  - Write file
  - Run engine [20%]
  - Render
  - Edit

## Design

The interface will eventually look something like this:

![image](https://user-images.githubusercontent.com/778856/125062911-cfc63b00-e0a6-11eb-9dfd-4f6fdbaa707f.png)

## Hacking

Najork is written in python and uses GTK4, Shapely (Python GEOS bindings), python-osc and not much else.


Install dependencies

 - `pipenv`
 - `(lib)gtk4-dev(el) >= 3.9`
 - `(lib)geos-dev(el) >= 3.3`

From project root:

```
pipenv install --dev
pipenv run make test
pipenv run make debug
```

### Packaging (WIP)

Eventually Najork will be packaged as a Flatpak, and for now will run
from a Flatpak build directory:

```
flatpak-builder ./build  com.verynoisy.najork.yml --force-clean
flatpak-builder --run ./build com.verynoisy.najork.yml /app/bin/najork
```

