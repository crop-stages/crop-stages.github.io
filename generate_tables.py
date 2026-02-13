#!/usr/bin/env python3
"""
Generate 93 crop HTML table pages from the template.
Each page is a self-contained HTML file with:
- Correct crop name + Latin name in <h1> and <title>
- Correct image paths: assets/images/crops/{slug}/stage-{n}.png
- Unique SEO meta tags
- English language (lang="en")
- BBCH stage descriptions specific to each crop type
- Desktop table + mobile cards layout
"""

import os
import html

# ============================================================
# CROP DATABASE: slug -> (display_name, latin_name, crop_type)
# crop_type determines which BBCH description set to use
# ============================================================

CROPS = {
    "alfalfa": ("Alfalfa", "Medicago sativa", "forage"),
    "artichoke": ("Artichoke", "Cynara cardunculus", "vegetable"),
    "arugula": ("Arugula", "Eruca vesicaria", "leafy"),
    "asparagus": ("Asparagus", "Asparagus officinalis", "vegetable"),
    "banana-musaceae": ("Banana", "Musa acuminata", "fruit_tropical"),
    "barley": ("Barley", "Hordeum vulgare", "cereal"),
    "bean": ("Bean", "Phaseolus vulgaris", "legume"),
    "bean-2": ("Bean", "Phaseolus vulgaris", "legume"),
    "bok-choy": ("Bok Choy", "Brassica rapa subsp. chinensis", "leafy"),
    "broccoli": ("Broccoli", "Brassica oleracea var. italica", "brassica"),
    "brussels-sprouts": ("Brussels Sprouts", "Brassica oleracea var. gemmifera", "brassica"),
    "buckwheat": ("Buckwheat", "Fagopyrum esculentum", "cereal"),
    "carrot": ("Carrot", "Daucus carota", "root"),
    "cauliflower": ("Cauliflower", "Brassica oleracea var. botrytis", "brassica"),
    "cayenne-pepper": ("Cayenne Pepper", "Capsicum annuum", "solanaceae"),
    "celery": ("Celery", "Apium graveolens", "vegetable"),
    "chickpea-2": ("Chickpea", "Cicer arietinum", "legume"),
    "chicory": ("Chicory", "Cichorium intybus", "leafy"),
    "chicory-2": ("Chicory", "Cichorium intybus", "leafy"),
    "clover": ("Clover", "Trifolium pratense", "forage"),
    "clover-2": ("Clover", "Trifolium pratense", "forage"),
    "common-vetch": ("Common Vetch", "Vicia sativa", "legume"),
    "corn": ("Corn", "Zea mays", "cereal"),
    "cotton": ("Cotton", "Gossypium hirsutum", "industrial"),
    "cotton-2": ("Cotton", "Gossypium hirsutum", "industrial"),
    "couch-grass": ("Couch Grass", "Elymus repens", "grass"),
    "cowpea": ("Cowpea", "Vigna unguiculata", "legume"),
    "cucumber": ("Cucumber", "Cucumis sativus", "cucurbit"),
    "daikon": ("Daikon", "Raphanus sativus var. longipinnatus", "root"),
    "dill": ("Dill", "Anethum graveolens", "herb"),
    "eggplant": ("Eggplant", "Solanum melongena", "solanaceae"),
    "fennel": ("Fennel", "Foeniculum vulgare", "herb"),
    "flax": ("Flax", "Linum usitatissimum", "industrial"),
    "flax-2": ("Flax", "Linum usitatissimum", "industrial"),
    "garlic": ("Garlic", "Allium sativum", "bulb"),
    "grape": ("Grape", "Vitis vinifera", "vine"),
    "grape-2": ("Grape", "Vitis vinifera", "vine"),
    "grape-3": ("Grape", "Vitis vinifera", "vine"),
    "grape-4": ("Grape", "Vitis vinifera", "vine"),
    "hemp": ("Hemp", "Cannabis sativa", "industrial"),
    "hemp-2": ("Hemp", "Cannabis sativa", "industrial"),
    "hops": ("Hops", "Humulus lupulus", "vine"),
    "kale": ("Kale", "Brassica oleracea var. sabellica", "brassica"),
    "kohlrabi": ("Kohlrabi", "Brassica oleracea var. gongylodes", "brassica"),
    "leek": ("Leek", "Allium ampeloprasum", "bulb"),
    "lentil": ("Lentil", "Lens culinaris", "legume"),
    "lettuce": ("Lettuce", "Lactuca sativa", "leafy"),
    "melon": ("Melon", "Cucumis melo", "cucurbit"),
    "oat": ("Oat", "Avena sativa", "cereal"),
    "oilseed-radish": ("Oilseed Radish", "Raphanus sativus var. oleiformis", "industrial"),
    "okra": ("Okra", "Abelmoschus esculentus", "vegetable"),
    "onion": ("Onion", "Allium cepa", "bulb"),
    "parsnip": ("Parsnip", "Pastinaca sativa", "root"),
    "pea": ("Pea", "Pisum sativum", "legume"),
    "pea-2": ("Pea", "Pisum sativum", "legume"),
    "peanut": ("Peanut", "Arachis hypogaea", "legume"),
    "peanut-2": ("Peanut", "Arachis hypogaea", "legume"),
    "pepper": ("Pepper", "Capsicum annuum", "solanaceae"),
    "pepper-2": ("Pepper", "Capsicum annuum", "solanaceae"),
    "perennial-ryegrass": ("Perennial Ryegrass", "Lolium perenne", "grass"),
    "perennial-ryegrass-2": ("Perennial Ryegrass", "Lolium perenne", "grass"),
    "pineapple": ("Pineapple", "Ananas comosus", "fruit_tropical"),
    "potato": ("Potato", "Solanum tuberosum", "tuber"),
    "potato-2": ("Potato", "Solanum tuberosum", "tuber"),
    "pumpkin": ("Pumpkin", "Cucurbita maxima", "cucurbit"),
    "quinoa": ("Quinoa", "Chenopodium quinoa", "cereal"),
    "radish": ("Radish", "Raphanus sativus", "root"),
    "rapeseed": ("Rapeseed", "Brassica napus", "oilseed"),
    "red-beet": ("Red Beet", "Beta vulgaris", "root"),
    "red-cabbage": ("Red Cabbage", "Brassica oleracea var. capitata f. rubra", "brassica"),
    "rice": ("Rice", "Oryza sativa", "cereal"),
    "rice-2": ("Rice", "Oryza sativa", "cereal"),
    "rutabaga": ("Rutabaga", "Brassica napus var. napobrassica", "root"),
    "sesame": ("Sesame", "Sesamum indicum", "oilseed"),
    "sorghum": ("Sorghum", "Sorghum bicolor", "cereal"),
    "soybean": ("Soybean", "Glycine max", "legume"),
    "soybean-2": ("Soybean", "Glycine max", "legume"),
    "soybean-3": ("Soybean", "Glycine max", "legume"),
    "spinach": ("Spinach", "Spinacia oleracea", "leafy"),
    "strawberry": ("Strawberry", "Fragaria × ananassa", "fruit_berry"),
    "sugar-beet": ("Sugar Beet", "Beta vulgaris subsp. vulgaris", "root"),
    "sugar-beet-2": ("Sugar Beet", "Beta vulgaris subsp. vulgaris", "root"),
    "sugarcane": ("Sugarcane", "Saccharum officinarum", "grass"),
    "sugarcane-2": ("Sugarcane", "Saccharum officinarum", "grass"),
    "sunflower": ("Sunflower", "Helianthus annuus", "oilseed"),
    "sweet-potato": ("Sweet Potato", "Ipomoea batatas", "tuber"),
    "tomato": ("Tomato", "Solanum lycopersicum", "solanaceae"),
    "tomato-2": ("Tomato", "Solanum lycopersicum", "solanaceae"),
    "turnip": ("Turnip", "Brassica rapa", "root"),
    "watermelon": ("Watermelon", "Citrullus lanatus", "cucurbit"),
    "wheat": ("Wheat", "Triticum aestivum", "cereal"),
    "white-cabbage": ("White Cabbage", "Brassica oleracea var. capitata", "brassica"),
    "white-mustard": ("White Mustard", "Sinapis alba", "oilseed"),
    "zucchini": ("Zucchini", "Cucurbita pepo", "cucurbit"),
}

# ============================================================
# BBCH STAGE DESCRIPTIONS BY CROP TYPE
# 10 stages: Germination, Sprouting, Emergence, Leaf dev,
#            Stem elongation, Inflorescence, Flowering,
#            Fruit dev, Ripening, Senescence
# ============================================================

BBCH_STAGES = {
    "default": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Sprouting", "Emergence", "Leaf Development", "Stem Elongation", "Inflorescence", "Flowering", "Fruit Development", "Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition",
            "Radicle emergence, seedling growth",
            "Shoot emergence, cotyledon unfolding",
            "Leaf unfolding, true leaves expand",
            "Stem elongation, shoot development",
            "Inflorescence emergence, bud formation",
            "Flowering, anthesis",
            "Fruit development and growth",
            "Fruit ripening, color change",
            "Plant senescence, drying"
        ],
        "alts": ["Seed", "Sprouting", "Emergence", "Leaf development", "Stem elongation", "Inflorescence", "Flowering", "Fruit development", "Ripening", "Senescence"]
    },
    "cereal": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Tillering", "Stem Elongation", "Booting", "Heading", "Flowering", "Grain Development", "Grain Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Coleoptile emergence, first leaves unfolding",
            "Tiller formation, side shoots develop",
            "Stem elongation, nodes visible",
            "Flag leaf sheath swelling, booting",
            "Head emergence from flag leaf sheath",
            "Anthesis, pollen release",
            "Grain filling, milk to dough stage",
            "Grain ripening, hard dough to maturity",
            "Plant drying, harvest ready"
        ],
        "alts": ["Seed", "Seedling", "Tillering", "Stem elongation", "Booting", "Heading", "Flowering", "Grain filling", "Grain ripening", "Senescence"]
    },
    "legume": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Sprouting", "Emergence", "Leaf Development", "Stem Elongation", "Bud Formation", "Flowering", "Pod Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, swelling",
            "Radicle emergence, hypocotyl growth",
            "Shoot emergence, cotyledon unfolding",
            "Leaf and tendril development",
            "Stem elongation, shoot growth",
            "Bud formation, inflorescence emergence",
            "Flowering, anthesis",
            "Pod formation and growth",
            "Seed ripening, pod yellowing",
            "Plant drying, senescence"
        ],
        "alts": ["Seed", "Sprouting", "Emergence", "Leaf development", "Stem elongation", "Bud formation", "Flowering", "Pod development", "Ripening", "Senescence"]
    },
    "solanaceae": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Shoot Growth", "Side Shoot Formation", "Bud Formation", "Flowering", "Fruit Development", "Fruit Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "True leaf unfolding, leaf expansion",
            "Main shoot elongation, branching",
            "Side shoot development, canopy formation",
            "Flower bud emergence, bud swelling",
            "Flowering, petal opening",
            "Fruit set and enlargement",
            "Fruit ripening, color change",
            "Plant senescence, leaf drop"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Shoot growth", "Branching", "Bud formation", "Flowering", "Fruit development", "Fruit ripening", "Senescence"]
    },
    "cucurbit": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Vine Growth", "Runner Formation", "Bud Formation", "Flowering", "Fruit Development", "Fruit Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, hypocotyl growth",
            "True leaf unfolding, leaf expansion",
            "Vine elongation, tendril formation",
            "Runner and lateral shoot development",
            "Flower bud formation, bud visible",
            "Male and female flowering",
            "Fruit set, fruit enlargement",
            "Fruit ripening, rind hardening",
            "Plant senescence, vine drying"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Vine growth", "Runner formation", "Bud formation", "Flowering", "Fruit development", "Fruit ripening", "Senescence"]
    },
    "root": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Root Thickening", "Harvestable Product", "Inflorescence", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "True leaf unfolding, rosette formation",
            "Tap root begins thickening",
            "Root reaches harvestable size",
            "Bolting, inflorescence emergence",
            "Flowering, anthesis",
            "Seed development in pods",
            "Seed ripening, pod drying",
            "Plant senescence, leaf yellowing"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Root thickening", "Harvestable root", "Inflorescence", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "brassica": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Head Formation", "Head Growth", "Inflorescence", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "True leaf unfolding, rosette formation",
            "Head or curd begins forming",
            "Head or curd enlargement",
            "Bolting, flower stalk emergence",
            "Flowering, anthesis",
            "Seed development in siliques",
            "Seed ripening, silique drying",
            "Plant senescence, drying"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Head formation", "Head growth", "Inflorescence", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "bulb": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Sprouting", "Leaf Development", "Bulb Formation", "Bulb Growth", "Inflorescence", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed or clove, imbibition",
            "Radicle or root emergence, sprout growth",
            "Leaf unfolding, leaf sheath development",
            "Bulb begins swelling",
            "Bulb enlargement, scale formation",
            "Flower stalk elongation, spathe visible",
            "Flowering, umbel opening",
            "Seed development",
            "Seed ripening, bulb maturity",
            "Leaf yellowing, neck softening"
        ],
        "alts": ["Seed/Clove", "Sprouting", "Leaf development", "Bulb formation", "Bulb growth", "Inflorescence", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "vine": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Dormancy", "Bud Break", "Leaf Development", "Shoot Growth", "Canopy Development", "Inflorescence", "Flowering", "Berry Development", "Berry Ripening", "Senescence"],
        "descriptions": [
            "Winter dormancy, bud scales closed",
            "Bud swelling, bud break, shoot emergence",
            "Leaf unfolding, leaves expand",
            "Shoot elongation, tendril development",
            "Canopy development, lateral shoots",
            "Inflorescence visible, flower clusters form",
            "Flowering, cap fall, fruit set",
            "Berry development, veraison onset",
            "Berry ripening, sugar accumulation",
            "Leaf fall, cane maturation"
        ],
        "alts": ["Dormancy", "Bud break", "Leaf development", "Shoot growth", "Canopy", "Inflorescence", "Flowering", "Berry development", "Berry ripening", "Senescence"]
    },
    "tuber": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Sprouting", "Emergence", "Leaf Development", "Stem Elongation", "Tuber Initiation", "Inflorescence", "Flowering", "Tuber Bulking", "Tuber Maturity", "Senescence"],
        "descriptions": [
            "Seed tuber dormancy break, sprout growth",
            "Shoot emergence from soil",
            "Leaf unfolding, canopy development",
            "Main stem elongation, branching",
            "Stolon development, tuber initiation",
            "Flower bud emergence",
            "Flowering, petal opening",
            "Tuber bulking, size increase",
            "Tuber maturity, skin set",
            "Haulm senescence, vine drying"
        ],
        "alts": ["Sprouting", "Emergence", "Leaf development", "Stem elongation", "Tuber initiation", "Inflorescence", "Flowering", "Tuber bulking", "Tuber maturity", "Senescence"]
    },
    "oilseed": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Rosette Formation", "Stem Elongation", "Stem Extension", "Bud Formation", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "Leaf unfolding, rosette formation",
            "Stem visible, internodes elongate",
            "Further stem extension, branching",
            "Flower buds visible, bud cluster tight",
            "Flowering, petals visible",
            "Pod development, seed filling",
            "Seed ripening, pod color change",
            "Plant drying, harvest ready"
        ],
        "alts": ["Seed", "Seedling", "Rosette", "Stem elongation", "Stem extension", "Bud formation", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "industrial": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Stem Elongation", "Vegetative Growth", "Bud Formation", "Flowering", "Fruit/Boll Development", "Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "True leaf development, leaf expansion",
            "Main stem elongation, node development",
            "Continued vegetative growth, branching",
            "Flower bud initiation, square formation",
            "Flowering, bloom opening",
            "Boll or capsule development",
            "Boll opening or capsule maturity",
            "Plant defoliation, senescence"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Stem elongation", "Vegetative growth", "Bud formation", "Flowering", "Boll/Capsule development", "Ripening", "Senescence"]
    },
    "forage": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Stem Elongation", "Vegetative Growth", "Bud Formation", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon or coleoptile emergence",
            "Leaf unfolding, trifoliate development",
            "Stem elongation, internode development",
            "Continued vegetative growth, branching",
            "Flower bud formation, bud visible",
            "Flowering, inflorescence open",
            "Seed set and development",
            "Seed ripening, pod maturation",
            "Plant senescence, regrowth potential"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Stem elongation", "Vegetative growth", "Bud formation", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "grass": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Tillering", "Stem Elongation", "Booting", "Heading", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Coleoptile emergence, first leaf",
            "Tiller formation, side shoots develop",
            "Stem elongation, nodes become visible",
            "Flag leaf sheath swelling",
            "Inflorescence emergence from sheath",
            "Anthesis, pollen release",
            "Caryopsis development, grain filling",
            "Grain ripening, maturation",
            "Plant drying, dormancy"
        ],
        "alts": ["Seed", "Seedling", "Tillering", "Stem elongation", "Booting", "Heading", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "leafy": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Rosette Growth", "Harvestable Product", "Inflorescence", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "True leaf unfolding, leaf expansion",
            "Rosette or head formation",
            "Leaves reach harvestable size",
            "Bolting, flower stalk elongation",
            "Flowering, anthesis",
            "Seed development",
            "Seed ripening, drying",
            "Plant senescence"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Rosette growth", "Harvestable leaves", "Inflorescence", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "herb": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Stem Elongation", "Vegetative Growth", "Bud Formation", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "True leaf unfolding, frond development",
            "Main stem elongation",
            "Continued vegetative growth, branching",
            "Flower bud initiation, umbel forming",
            "Flowering, umbel opening",
            "Seed development on umbels",
            "Seed ripening, drying",
            "Plant senescence, drying"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Stem elongation", "Vegetative growth", "Bud formation", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
    "fruit_tropical": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Planting", "Sprouting", "Leaf Development", "Vegetative Growth", "Sucker Formation", "Inflorescence", "Flowering", "Fruit Development", "Fruit Ripening", "Senescence"],
        "descriptions": [
            "Planting material, initial root growth",
            "Shoot emergence, first leaves",
            "Leaf unfolding, leaf expansion",
            "Continued vegetative growth",
            "Sucker or ratoon formation",
            "Inflorescence emergence, bud visible",
            "Flowering, petal opening",
            "Fruit development and enlargement",
            "Fruit ripening, color change",
            "Plant senescence, harvest"
        ],
        "alts": ["Planting", "Sprouting", "Leaf development", "Vegetative growth", "Sucker formation", "Inflorescence", "Flowering", "Fruit development", "Fruit ripening", "Senescence"]
    },
    "fruit_berry": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Dormancy", "Crown Growth", "Leaf Development", "Runner Formation", "Stolon Growth", "Inflorescence", "Flowering", "Fruit Development", "Fruit Ripening", "Senescence"],
        "descriptions": [
            "Dormancy, crown planting",
            "Crown growth, first leaves emerging",
            "Leaf unfolding, trifoliate leaves expand",
            "Runner formation begins",
            "Stolon elongation, daughter plants",
            "Inflorescence emergence from crown",
            "Flowering, petal opening",
            "Fruit set, green fruit enlargement",
            "Fruit ripening, color change",
            "Leaf senescence, dormancy onset"
        ],
        "alts": ["Dormancy", "Crown growth", "Leaf development", "Runner formation", "Stolon growth", "Inflorescence", "Flowering", "Fruit development", "Fruit ripening", "Senescence"]
    },
    "vegetable": {
        "codes": ["00–09", "10–19", "20–29", "30–39", "40–49", "51–59", "60–69", "70–79", "80–89", "90–99"],
        "names": ["Germination", "Seedling Growth", "Leaf Development", "Shoot Growth", "Harvestable Product", "Inflorescence", "Flowering", "Seed Development", "Seed Ripening", "Senescence"],
        "descriptions": [
            "Dry seed, imbibition, radicle emergence",
            "Cotyledon emergence, seedling growth",
            "True leaf unfolding, leaf expansion",
            "Main shoot elongation, branching",
            "Harvestable product development",
            "Flower bud emergence",
            "Flowering, anthesis",
            "Seed development",
            "Seed ripening",
            "Plant senescence"
        ],
        "alts": ["Seed", "Seedling", "Leaf development", "Shoot growth", "Harvestable product", "Inflorescence", "Flowering", "Seed development", "Seed ripening", "Senescence"]
    },
}


def get_bbch(crop_type):
    """Get BBCH data for a crop type, fallback to default."""
    return BBCH_STAGES.get(crop_type, BBCH_STAGES["default"])


def generate_crop_html(slug, display_name, latin_name, crop_type):
    """Generate a complete self-contained HTML page for one crop."""
    bbch = get_bbch(crop_type)
    codes = bbch["codes"]
    names = bbch["names"]
    descriptions = bbch["descriptions"]
    alts = bbch["alts"]

    dn = html.escape(display_name)
    ln = html.escape(latin_name)
    slug_e = html.escape(slug)

    # Build image cells for desktop
    img_cells = []
    for i in range(1, 11):
        alt = html.escape(alts[i-1])
        img_cells.append(f'        <td><img src="../assets/images/crops/{slug_e}/{slug_e}_stage_{i}.png" alt="{dn} Stage {i} — {alt}"></td>')
    img_row = "\n".join(img_cells)

    # Build BBCH code cells
    bbch_cells = []
    for c in codes:
        bbch_cells.append(f'        <td class="bbch">{c}</td>')
    bbch_row = "\n".join(bbch_cells)

    # Build description cells
    desc_cells = []
    for d in descriptions:
        desc_cells.append(f'        <td>{html.escape(d)}</td>')
    desc_row = "\n".join(desc_cells)

    # Build product placeholder cells
    placeholder_cells = []
    for _ in range(10):
        placeholder_cells.append('        <td><span class="placeholder">Add product name &amp;&nbsp;dosage</span></td>')
    placeholder_row = "\n".join(placeholder_cells)

    # Build mobile cards
    mobile_cards = []
    for i in range(10):
        alt = html.escape(alts[i])
        mobile_cards.append(f"""    <div class="mobile-card">
        <img src="../assets/images/crops/{slug_e}/{slug_e}_stage_{i+1}.png" alt="{dn} Stage {i+1} — {alt}">
        <div class="info">
            <div class="stage-name">{html.escape(descriptions[i])}</div>
            <div class="bbch-code">BBCH {codes[i]}</div>
            <div class="product-hint">Add product</div>
        </div>
    </div>""")
    mobile_html = "\n".join(mobile_cards)

    # Keywords
    name_lower = display_name.lower()
    kw = f"{name_lower} BBCH, {name_lower} growth stages, fertilizer timing {name_lower}, {latin_name}"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{dn} Growth Stages (BBCH) | Crop Stages</title>
<meta name="description" content="Professional BBCH growth stage illustrations for {dn} ({ln}). 10 stages from germination to maturity.">
<meta name="keywords" content="{html.escape(kw)}">
<link rel="canonical" href="https://crop-stages.github.io/crops/{slug_e}.html">

<style>

* {{
    box-sizing: border-box;
}}

body {{
    font-family: "Segoe UI", Arial, sans-serif;
    background: #ffffff;
    margin: 0;
    padding: 40px;
    color: #4a4f45;
}}

.header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 40px;
    flex-wrap: wrap;
    gap: 10px;
}}

.header h1 {{
    font-weight: 400;
    font-size: clamp(24px, 4vw, 42px);
    margin: 0;
    color: #6c7466;
}}

.header .right-title {{
    font-size: clamp(12px, 1.4vw, 16px);
    letter-spacing: 1px;
    color: #6c7466;
}}

.nav-link {{
    display: inline-block;
    margin-bottom: 20px;
    color: #5a7a52;
    text-decoration: none;
    font-size: 14px;
}}
.nav-link:hover {{
    text-decoration: underline;
}}

/* === TABLE LAYOUT === */
.stages-table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}}

.stages-table .label-col {{
    width: 140px;
}}

.stages-table tr.image-row td {{
    vertical-align: bottom;
    text-align: center;
    padding: 10px 2px 15px;
    position: relative;
}}

.stages-table tr.image-row td:not(:first-child):not(:last-child)::after {{
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
    border-right: 2px dashed #c5cbbe;
}}

.stages-table tr.image-row td img {{
    max-width: 100%;
    max-height: 220px;
    height: auto;
    display: block;
    margin: 0 auto;
}}

.stages-table tr.data-row td {{
    padding: 10px 5px;
    font-size: clamp(9px, 1.1vw, 14px);
    text-align: center;
    vertical-align: top;
    border-top: 1px solid #c8cec0;
    line-height: 1.35;
    overflow-wrap: break-word;
    word-wrap: break-word;
    hyphens: auto;
}}

.stages-table tr.data-row:first-of-type td {{
    border-top: 2px solid #b7bdad;
}}

.stages-table tr.data-row td.label {{
    text-align: left;
    font-weight: 600;
    color: #6c7466;
    padding-right: 10px;
}}

.stages-table tr.data-row td.bbch {{
    font-size: clamp(11px, 1.3vw, 16px);
    font-weight: 500;
}}

.stages-table tr.data-row.footer-row td {{
    min-height: 40px;
}}

.stages-table tr.data-row.footer-row td .placeholder {{
    color: #c8cec0;
    font-size: clamp(8px, 0.9vw, 11px);
    font-style: italic;
    line-height: 1.3;
}}

/* === RESPONSIVE === */
@media (max-width: 1100px) {{
    .stages-table .label-col {{
        width: 110px;
    }}
}}

@media (max-width: 800px) {{
    body {{
        padding: 20px;
    }}
    .stages-table .label-col {{
        width: 90px;
    }}
    .stages-table tr.image-row td img {{
        max-height: 140px;
    }}
}}

@media (max-width: 540px) {{
    body {{
        padding: 16px;
    }}
    .stages-table {{
        display: none;
    }}
    .mobile-cards {{
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}
    .mobile-card {{
        background: #f6f7f5;
        border-radius: 10px;
        padding: 14px;
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .mobile-card img {{
        width: 70px;
        height: auto;
        flex-shrink: 0;
    }}
    .mobile-card .info {{
        font-size: 14px;
        line-height: 1.5;
    }}
    .mobile-card .info .stage-name {{
        font-weight: 600;
        font-size: 14px;
        color: #4a4f45;
    }}
    .mobile-card .info .bbch-code {{
        color: #9da39a;
        font-size: 12px;
    }}
    .mobile-card .info .product-hint {{
        color: #c8cec0;
        font-size: 11px;
        font-style: italic;
        margin-top: 4px;
    }}
}}

@media (min-width: 541px) {{
    .mobile-cards {{
        display: none;
    }}
}}

</style>
</head>

<body>

<a href="../index.html" class="nav-link">&larr; Back to all crops</a>

<div class="header">
    <h1>{dn} ({ln})</h1>
    <div class="right-title">Botanical Growth Stages</div>
</div>

<!-- ===== DESKTOP TABLE ===== -->
<table class="stages-table">
    <colgroup>
        <col class="label-col">
        <col><col><col><col><col><col><col><col><col><col>
    </colgroup>

    <tr class="image-row">
        <td></td>
{img_row}
    </tr>

    <tr class="data-row">
        <td class="label">BBCH Stage</td>
{bbch_row}
    </tr>

    <tr class="data-row">
        <td class="label">Description</td>
{desc_row}
    </tr>

    <tr class="data-row footer-row">
        <td class="label">Your Product</td>
{placeholder_row}
    </tr>
</table>

<!-- ===== MOBILE CARDS ===== -->
<div class="mobile-cards">
{mobile_html}
</div>

</body>
</html>"""
    return page


def main():
    # Output directory
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crops")
    os.makedirs(out_dir, exist_ok=True)

    count = 0
    for slug, (display_name, latin_name, crop_type) in sorted(CROPS.items()):
        page_html = generate_crop_html(slug, display_name, latin_name, crop_type)
        filepath = os.path.join(out_dir, f"{slug}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(page_html)
        count += 1

    print(f"Generated {count} crop table pages in {out_dir}/")
    return count


if __name__ == "__main__":
    main()
