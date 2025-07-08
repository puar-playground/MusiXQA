from dataclasses import dataclass, asdict
import yaml

@dataclass
class MusicConfig:
    title_str: str = 'Generated-Music'
    author_str: str = ''
    scale_type: str = 'Major'
    scale_root: str = 'C'
    encode_format: str = 'beat'
    treble: bool = True
    bass: bool = True
    n_bar: int = 20
    bpm: int = 90
    meterfrac: tuple = (4, 4)
    parindent: int = 0
    instrument: str = ''
    spacing: int = 0
    smallmusicsize: bool = True
    barnumber_format: str = 'system'
    show_chord: bool = True
    repeat_interval: tuple = None

    def save(self, file_path: str):
        """Save the configuration to a YAML file."""
        with open(file_path, 'w') as file:
            yaml.dump(asdict(self), file)

    @classmethod
    def load(cls, file_path: str):
        """Load the configuration from a YAML file."""
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return cls(**data)

# Using the configuration
if __name__ == "__main__":
    # Create an instance
    config = MusicConfig(title_str="Symphony No. 9")

    # Save it to a file
    config.save("music_config.yaml")

    loaded_config = MusicConfig.load("music_config.yaml")
    print(loaded_config)

    
    