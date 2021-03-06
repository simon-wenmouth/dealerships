
dealerships
===========

A set of quick-and-dirty scripts used build a list of automotive dealerships in the USA.

Installation
------------

.. code-block:: shell

    git clone https://github.com/simon-wenmouth/dealerships.git

    cd dealerships

    virtualenv venv

    source venv/bin/activate

    pip install -r requirements.txt

Usage
-----

On a per manufacturer basis run the download scripts, i.e.

.. code-block:: shell

    cd dealerships/manufacturers/lincoln/

    ./download_data.py

    less ../../../data/lincoln.json

Notes
-----

This repository contains the data these manufacturer's dealerships.

+---------------+------------------+
| Make          | Dealership Count |
+===============+==================+
| Acura         | 272              |
+---------------+------------------+
| Audi          | 276              |
+---------------+------------------+
| BMW           | 338              |
+---------------+------------------+
| Buick         | 1994             |
+---------------+------------------+
| Cadillac      | 914              |
+---------------+------------------+
| Chevrolet     | 2919             |
+---------------+------------------+
| Chrysler      | 2609             |
+---------------+------------------+
| Dodge         | 2609             |
+---------------+------------------+
| Fiat          | 2607             |
+---------------+------------------+
| Ford          | 2937             |
+---------------+------------------+
| GMC           | 1690             |
+---------------+------------------+
| Hyundai       | 631              |
+---------------+------------------+
| Infiniti      | 207              |
+---------------+------------------+
| Jaguar        | 165              |
+---------------+------------------+
| Jeep          | 2609             |
+---------------+------------------+
| Kia           | 761              |
+---------------+------------------+
| Lexus         | 234              |
+---------------+------------------+
| Lincoln       | 905              |
+---------------+------------------+
| Mercedes-Benz | 372              |
+---------------+------------------+
| Mini          | 121              |
+---------------+------------------+
| Mitsubishi    | 318              |
+---------------+------------------+
| Nissan        | 1056             |
+---------------+------------------+
| Porsche       | 189              |
+---------------+------------------+
| Ram           | 2609             |
+---------------+------------------+
| Scion         | 924              |
+---------------+------------------+
| Smart         | 87               |
+---------------+------------------+
| Subaru        | 624              |
+---------------+------------------+
| Toyota        | 1205             |
+---------------+------------------+
| Volkswagen    | 645              |
+---------------+------------------+
| Volvo         | 297              |
+---------------+------------------+

NADA_ reports that there were 16K (or so) new car dealerships and the total of the above table
is greater than 20K which means that there are dealerships with multiple franchises (i.e. they
are in more than one file).

As such, I have merged the various manufacturers into a single normalized file (based on URL)
which has identified 19,171 different dealerships.  Evidently a better heuristic is required.

.. _NADA: https://www.nada.org/IndustryAnalysis/_Resources/2015/NADA-DATA-2014/

Changelog
---------

* 2015-05-29
  Initial revision pushed to GitHub.

* 2015-05-31
  Created normalized JSON files.

* 2015-06-01
  Created normalized CSV files.

* 2015-06-03
  Added CSV files containing
  - DNS record data
  - Web sites meta-data
  for various dealer sites I was able to identify through the DNS system.

* 2015-06-05
  Initial revision of dealership list that are hosted by Cobalt Nitra (4721 sites).

* 2015-06-06
  - Initial revision of dealership list that are hosted by Clickmotive (2471 sites).
  - Initial revision of dealership list that are hosted by Dealer.com (9731 sites).
  - Initial revision of dealership list that are hosted by DealerFire.com (199 of 351 sites).

