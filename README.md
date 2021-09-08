# NAJORK

Womble, muck and sneedball inspired musical scores.

![image](https://user-images.githubusercontent.com/778856/125062656-8bd33600-e0a6-11eb-8fa9-47292c8074ca.png)

Najork *will be* a geometric, kinetic composition environment for music, and anything else that can consume OSC events (lighting, installations).

It takes its inspiration from the veritable [Iannix](https://www.iannix.org/) with a focus on periodic events and modulations linked to articulated constructions.

By parenting mechanisms and objects to each other all sorts of unpredicatable relationships can be translated into musical rhythms and patterns (listener enjoyment not guaranteed).

Najork does not create sound, it is a note and parameter source for a sound producing application, such as a DAW or modular system.

## Project status

  - Models [90%]
  - Read file [70%]
  - Write file
  - Run engine [80%]
  - Render [15%]
  - Edit

## Design

The interface will eventually look something like this:

![image](https://user-images.githubusercontent.com/778856/125062911-cfc63b00-e0a6-11eb-9dfd-4f6fdbaa707f.png)

## Hacking

Najork is written in python and uses GTK4, Shapely (Python GEOS bindings), oscpy and not much else.


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

Eventually Najork will be packaged as a Flatpak, and for now may run
from a Flatpak build directory:

```
flatpak-builder ./build  com.verynoisy.najork.yml --force-clean
flatpak-builder --run ./build com.verynoisy.najork.yml /app/bin/najork
```

