# dzetsaka : classification tool
![Inselberg in Guiana Amazonian Park](https://cdn.rawgit.com/lennepkade/dzetsaka/master/img/guyane.jpg)

dzetsaka <img src="https://cdn.rawgit.com/lennepkade/dzetsaka/master/img/icon.png" alt="dzetsaka logo" width="30px"/> is very fast and easy to use but also a **powerful classification plugin for Qgis**. Based on Gaussian Mixture Model classifier developped by  [Mathieu Fauvel](http://fauvel.mathieu.free.fr), this plugin is a more generalist tool than [Historical Map](https://github.com/lennepkade/HistoricalMap) which was dedicated to classify forests from old maps.
This plugin has by developped by [Nicolaï Van Lennepkade](http://www.lennepka.de/) (aka Nicolas Karasiak).

## What does dzetsaka mean ?
As this tool was developped during my work in the Guiana Amazonian Park to classify different kind of vegetation, I gave an Teko name (a native-american language from a nation which lives in french Guiana) which represent the objects we use to see the world through, such as satellites, microscope, camera... 

## Discover the magic of dzetsaka
`dzetsaka : Classification tool` runs with scipy library. You can download package like [Spider by Anaconda](https://docs.continuum.io/anaconda/) for a very easy setup. 

Then, as this plugin is very simple, you will just need two things for making a good classification : 
- A **raster**
- A **shapefile** which contains your **ROI** (Region Of Interest)

The shapefile must have a column which contains your classification numbers *(1,3,4...)*. Otherwise if you use text or anything else it certainly won't work.

## Tips

- If your raster is *spot6scene.tif*, you can create your mask under the name *spot6scene_mask.tif* and the script will detect it automatically.
- If you want to keep your spectral ROI model from an image, you can save your model to use it on another image.

## Todo
- Generate confusion matrix on demand
- Implement different but fast classifiers. Badly those in scikit (like Random Forest or SVM) took hours to classify.

### Thanks to...
I would like to thank the [Guiana Amazonian Park](http://www.parc-amazonien-guyane.fr/) for their confidence in my work, and my school formation [Sigma](http://sigma.univ-toulouse.fr/en/welcome.html) for their excellent lessons in geomatics.

<img height="30px" src="https://rawgit.com/lennepkade/dzetsaka/master/img/logo-pag.jpg" alt="Parc amazonien de Guyane"/>
<img height="30px" src="https://raw.githubusercontent.com/lennepkade/HistoricalMap/master/img/dynafor.gif" alt="Dynafor"/>
<img height="30px" src="https://raw.githubusercontent.com/lennepkade/HistoricalMap/master/img/ensat.gif" alt="ENSAT"/>
<img height="30px" src="https://raw.githubusercontent.com/lennepkade/HistoricalMap/master/img/ut2j.png" alt="UT2J"/>
<img height="30px" src="https://raw.githubusercontent.com/lennepkade/HistoricalMap/master/img/sigma.gif" alt="Sigma"/>