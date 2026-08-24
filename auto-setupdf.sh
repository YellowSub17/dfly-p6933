
dragonfly.init -t cp512-rb2
dragonfly.init -t cp256-rb1


python setup_df.py --df-tag cp256-rb1_0001 --hit-tags ./hits/r0306_cp256-rb1 ./hits/r0307_cp256-rb1 --detd 214 --lamb 1.26 | bash
python setup_df.py --df-tag cp512-rb2_0001 --hit-tags ./hits/r0306_cp512-rb2 ./hits/r0307_cp512-rb2 --detd 214 --lamb 1.26 | bash
