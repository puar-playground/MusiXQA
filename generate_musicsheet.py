import random
from util.musixtex_util import generate_music, compile_musicpdf
from util.config_util import MusicConfig
from util.random_util import weighted_sample, generate_name, generate_title
from util.scale_util import scales_dict
from util.pdf_util import pdf_to_images, get_pdf_page_count
from itertools import product
from tqdm import tqdm
import argparse

import os
os.system('clear')

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", default='./data/new', help="data_dir", type=str)
parser.add_argument("--batch_index", default=0, help="batch_index", type=int)
parser.add_argument("--n_epoch", default=100, help="n_epoch", type=int)
args = parser.parse_args()


if __name__=='__main__':


    # Generate initial settings and sort by the first element (epoch)
    settings = sorted(product(range(args.n_epoch), ["Major", "Minor"], ["note", "beat"]), key=lambda x: x[0])

    # Expand settings by iterating over scale roots
    settings_expand = [
        [epoch, scale_type, encode_format, scale_root]
        for epoch, scale_type, encode_format in settings
        for scale_root in sorted(scales_dict[scale_type].keys())
    ]

    n_data = len(settings_expand)

    pbar = tqdm(enumerate(settings_expand), total=n_data, ncols=120)

    for i, (epoch, scale_type, encode_format, scale_root) in pbar:
        
        bpm = weighted_sample(range(50, 140),  k=1, weights='uniform')[0]
        n_beat = weighted_sample([2, 3, 4],  k=1, weights=[1, 2, 2])[0]
        spacing = weighted_sample([0, 1, 2, 3],  k=1, weights='uniform')[0]
        barnumber_format = weighted_sample(['system', 'default'],  k=1, weights='uniform')[0]
        treble, bass = weighted_sample([[True, True], [True, False], [False, True]],  k=1, weights=[4, 3, 1])[0]
        instrument = ''
        parindent = 0

        if treble and bass:
            smallmusicsize = True
        else:
            smallmusicsize = weighted_sample([True, False],  k=1, weights='uniform')[0]

        show_chord = random.choice([True, False])
        scale_root_mod = scale_root.replace('#', '\\#')
        
        # define saving directory and name
        data_id = f'{str(i + n_data * args.batch_index).zfill(7)}'
        save_dir = os.path.join(args.data_dir, data_id)

        if os.path.isfile(os.path.join(save_dir, f'{data_id}.png')):
            continue

        # Your processing logic here
        pbar.set_description(f'{epoch=}, {data_id=}, {encode_format}, {scale_root}, {scale_type}')

        n_bar = weighted_sample(range(10, 20),  k=1, weights='uniform')[0]

        n_page = 0
        while True:

            repeat = random.choice([True, False])
            if repeat:
                repeat_s, repeat_e = sorted(random.sample(range(1, n_bar), k=2))
                repeat_interval = (repeat_s, repeat_e)
            else:
                repeat_interval = None

            # Set configuration file
            config = MusicConfig(title_str=generate_title(), author_str=generate_name(), scale_type=scale_type,
                            scale_root=scale_root, encode_format=encode_format, treble=treble, bass=bass,
                            n_bar=n_bar, bpm=bpm, meterfrac=[n_beat, 4], spacing=spacing, repeat_interval=repeat_interval,
                            show_chord=show_chord, barnumber_format=barnumber_format, instrument=instrument, 
                            smallmusicsize=smallmusicsize, parindent=parindent)

            # Generate music in latex format and save ground truth in a MusicComposition instance
            while True:
                try:
                    MusixTex_str, music_data = generate_music(config)
                    break
                except:
                    continue

            # Compile MusixTex to PDF
            compile_musicpdf(MusixTex_str, save_dir=os.path.join(save_dir, 'latex'))
            n_page = get_pdf_page_count(os.path.join(save_dir, 'latex', 'music_sheet.pdf'))

            # We focus on single page VQA, so, if the pdf has more than 1 page, try generate less bars.
            if n_page != 1:
                n_bar += -1
            else:
                break

        config.save(os.path.join(save_dir, f'{data_id}_config.yaml'))

        music_data.to_json(file_dir=save_dir, file_name=data_id)
        music_data.to_midi(file_dir=save_dir, file_name=data_id, audio=False)

        pdf_to_images(pdf_path=os.path.join(save_dir, 'latex', 'music_sheet.pdf'), output_folder=save_dir, image_name=data_id)

        break