"""V27 missing-role art brief. Do not overwrite the already accepted four.
Ages/wardrobe reflect the 8-character brief. Heights are existing project art
choices, not user-provided measurements. All models remain visual-review pilots.
"""
PROFILES={
'oldman':dict(label='騎樓阿伯',age_text='80歲',height=1.60,
 macro=dict(gender=.99,age=.98,weight=.34,muscle=.19,height=.42,proportions=.48),
 face=[('head-scale-horiz-decr',.34),('chin-width-decr',.25),('chin-prominent-incr',.20),('nose-width1-incr',.37),('nose-scale-depth-incr',.55),('mouth-scale-horiz-decr',.12),('l-eye-scale-decr',.28),('r-eye-scale-decr',.28),('l-cheek-volume-decr',.28),('r-cheek-volume-decr',.26),('head-age-incr',.65),('l-eye-bag-incr',.46),('r-eye-bag-incr',.43),('mouth-laugh-lines-out',.35)],
 skin='old_asian_male.mhmat',hair='short04.mhclo',hair_color=(.49,.52,.55),
 shirt='toigo_basic_tucked_t-shirt.mhclo',pants='toigo_wool_pants.mhclo',
 top=(.035,.12,.075),bottom=(.13,.135,.12),pattern=False,
 accessories=['baseball_cap','smartphone'],note='灰白短髮、墨綠T恤、獨立鴨舌帽、手持手機；握持手勢須目視驗收'),
'cop':dict(label='警察大哥',age_text='30多歲',height=1.79,
 macro=dict(gender=.99,age=.58,weight=.50,muscle=.72,height=.64,proportions=.53),
 face=[('head-square',.63),('chin-width-incr',.34),('chin-prominent-incr',.24),('nose-scale-depth-incr',.20),('nose-width1-decr',.17),('mouth-scale-horiz-incr',.11),('l-eye-scale-decr',.08),('r-eye-scale-decr',.08),('l-cheek-volume-incr',.16),('r-cheek-volume-incr',.16)],
 skin='young_asian_male.mhmat',hair='short01.mhclo',hair_color=(.055,.065,.08),
 shirt='namuhekam_male_polo_shirt.mhclo',pants='toigo_wool_pants.mhclo',
 top=(.30,.51,.65),bottom=(.023,.037,.066),pattern=False,
 accessories=['generic_peaked_cap','radio','uniform_details'],note='淺藍制服、短黑髮與獨立大盤帽；只用泛用幾何標記，無真實警徽/單位/姓名'),
'shui':dict(label='阿水伯',age_text='60多歲',height=1.66,
 macro=dict(gender=.99,age=.86,weight=.49,muscle=.34,height=.47,proportions=.49),
 face=[('head-round',.31),('head-scale-horiz-incr',.16),('chin-width-decr',.12),('nose-width1-incr',.56),('nose-point-width-incr',.32),('mouth-scale-horiz-incr',.26),('l-eye-scale-decr',.15),('r-eye-scale-decr',.15),('l-cheek-volume-incr',.25),('r-cheek-volume-incr',.22),('head-age-incr',.37),('l-eye-bag-incr',.26),('r-eye-bag-incr',.24),('mouth-laugh-lines-out',.42)],
 skin='old_asian_male.mhmat',hair='short02.mhclo',hair_color=(.38,.39,.38),
 shirt='namuhekam_male_polo_shirt.mhclo',pants='cortu_cargo_pants.mhclo',
 top=(.51,.23,.055),bottom=(.13,.15,.09),pattern=True,
 accessories=['straw_hat','glasses','shoulder_towel'],note='灰髮、獨立草帽、眼鏡與肩披毛巾，褐橘花衫；花衫初版沿用CC0有領上衣而非已完成開襟夏威夷版型'),
'bro':dict(label='隔壁攤大哥',age_text='40歲',height=1.80,
 macro=dict(gender=1.,age=.67,weight=.84,muscle=.91,height=.64,proportions=.55),
 face=[('head-square',.92),('head-scale-horiz-incr',.54),('chin-width-incr',.70),('chin-prominent-incr',.45),('nose-width1-incr',.17),('nose-scale-depth-incr',.18),('mouth-scale-horiz-incr',.39),('l-eye-scale-decr',.24),('r-eye-scale-decr',.24),('l-cheek-volume-incr',.38),('r-cheek-volume-incr',.36),('head-age-incr',.10)],
 skin='young_asian_male.mhmat',hair=None,hair_color=None,
 shirt='namuhekam_male_polo_shirt.mhclo',pants='cortu_cargo_pants.mhclo',
 top=(.45,.035,.027),bottom=(.025,.027,.032),pattern=True,
 accessories=['white_headband','gold_chain'],note='光頭、壯碩身形、紅色花衫、白頭巾與獨立金鍊；花衫版型仍為候選')}
REQUIRED_BONES={'Root','pelvis','spine_01','spine_02','spine_03','neck_01','head','upperarm_l','upperarm_r','lowerarm_l','lowerarm_r','hand_l','hand_r','thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r'}
REQUIRED_KEYS={'mouthOpen','mouthSmile','mouthFrown','eyeBlinkLeft','eyeBlinkRight','browDownLeft','browDownRight','browInnerUp'}
