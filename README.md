# NAJORK

Womble, muck and sneedball for your music.

![image](https://user-images.githubusercontent.com/778856/125062656-8bd33600-e0a6-11eb-8fa9-47292c8074ca.png)

Najork is a geometric, kinetic composition environment for music, and anything else that can consume OSC events.

It takes its inspiration from the veritable [Iannix](https://www.iannix.org/) with a focus on generated timings linked to articulated constructions.

By parenting mechanisms and objects to each other all sorts of interesting relationships can be translated in music (listener enjoyment not guaranteed).

## Hacking

This application currently runs in a Flatpak. Simply:

```
git clone git@github.com:mrmonkington/najork.git
cd najork
flatpak-builder ./build  com.verynoisy.najork.yml --force-clean
flatpak-builder --run ./build com.verynoisy.najork.yml /app/bin/najork
```

It's written in python using GTK4, python-osc and not much else.

More to follow...
