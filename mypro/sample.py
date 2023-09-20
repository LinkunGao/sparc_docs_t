"""Sample module documentation"""

class Sample(object):

    # count = 0
    # _dataset_path: Path = Path('./')
    # _metadata: Metadata = None
    # _manifest_metadata: Metadata = None
    # _previous_sub_id = ""


    def __init__(self):
        self.sample_id = ""
        self.subject_id = ""
        self.sample_dir = Path()
        self.source_sample_paths: List[Path] = []
        self.index = -1

    def set_subject_id(self, sub_id):
        """
        set subject id to sample object
        :param sub_id: a subject id
        :type sub_id: str
        """
        self.subject_id = sub_id
        if sub_id != Sample._previous_sub_id:
            Sample._previous_sub_id = sub_id
            Sample.count = 0
        self._generate_sample_path_and_id()

    def _generate_sample_path_and_id(self):
        """
        Generate sample path and id
        """
        subject_dir = self._dataset_path.joinpath("primary", self.subject_id)
        if subject_dir.exists():
            sub_dirs = []
            for sub_dir in subject_dir.iterdir():
                if sub_dir.is_dir():
                    sub_dirs.append(sub_dir.name)
            while True:
                Sample.count += 1
                self.sample_id = f"sam-{Sample.count}"
                if self.sample_id not in sub_dirs:
                    break
        else:
            Sample.count += 1
            self.sample_id = f"sam-{Sample.count}"

        self.sample_dir = subject_dir.joinpath(self.sample_id)
        self._add_sample_row()

    def get_sample_id(self):
        """
        Get sample id
        :return: sample id
        """
        return self.sample_id

    def _add_sample_row(self):
        """
        Add row in sample metadata
        """
        df = self._metadata.data
        if self.sample_id in df['sample id'].values and self.subject_id in df['subject id']:
            self.index = df.loc[df['sample id'] == self.sample_id].index[0]
        else:
            sample = [self.sample_id, self.subject_id] + [float('nan')] * (len(df.columns) - 2)
            # Create new row
            self.index = len(df)
            df.loc[self.index] = sample

    def add_path(self, source_path):
        """
        Add sample source path to sample object

        :param source_path: sample folder source path
        :type source_path: str | list

        """
        if isinstance(source_path, list):
            for file_path in source_path:
                self.source_sample_paths.append(Path(file_path))
        else:
            self.source_sample_paths.append(Path(source_path))


    def set_path(self, source_path):
        """
        Add sample source path to sample object
        Override the Previous path

        :param source_path: sample folder source path
        :type source_path: str | list

        """
        if isinstance(source_path, list):
            self.source_sample_paths = []
            for file_path in source_path:
                self.source_sample_paths.append(Path(file_path))
        else:
            self.source_sample_paths = [Path(source_path)]


    def set_values(self, metadata={}):
        """
        :param metadata: key : value dict (element:value)
        :type metadata: dict
        """
        if not isinstance(metadata, dict):
            msg = f"You should use a dict here, you provide parameter type is {type(metadata)}"
            raise TypeError(msg)

        for element, value in metadata.items():
            if element == 'sample id' or element == 'subject id':
                continue
            else:
                self.set_value(element, value)

    def set_value(self, element, value):
        """
        Set value for one element for a sample

        :param element: element in sample metadata file
        :type element: str
        :param value: the values for that element
        :type value: str|int

        """
        df = self._metadata.data
        index = df.loc[(df['sample id'] == self.sample_id) & (df['subject id'] == self.subject_id)].index[0]
        element = find_col_element(element, self._metadata)
        if index == self.index:
            df.loc[index, element] = value

        self.save()

    def move(self):
        """
        Move sample files from source dir to dataset primary dir

        """
        if not self.sample_dir.exists():
            self.sample_dir.mkdir(parents=True, exist_ok=True)

        for source_sam in self.source_sample_paths:
            if source_sam.is_dir():
                source_sample_files = source_sam.rglob("*")
                for file in source_sample_files:
                    if file.is_file():
                        relative_path = file.relative_to(source_sam)
                        target_file = self.sample_dir / relative_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(str(file), str(target_file))
                        self._update_manifest(sample_path=str(target_file))
            elif source_sam.is_file():
                shutil.copy(str(source_sam), str(self.sample_dir))
                self._update_manifest(sample_path=str(self.sample_dir / source_sam.name))
    def _update_manifest(self, sample_path):
        """
        Update manifest metadata, after remove samples

        :param sample_path: sample path
        :type sample_path: str
        """
        file_path = Path(
            sample_path.replace(str(self._dataset_path), '')[1:]).as_posix()

        row = {
            'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            'description': f"File of subject {self.subject_id} sample {self.sample_id}",
            'file type': Path(sample_path).suffix
        }

        df_manifest = self._manifest_metadata.data
        # check is exist
        if file_path in df_manifest['filename'].values:
            manifest_index = df_manifest.loc[df_manifest['filename'] == file_path].index[0]
        else:
            manifest_row = [file_path] + [float('nan')] * (len(df_manifest.columns) - 1)
            # Create new row
            manifest_index = len(df_manifest)
            df_manifest.loc[manifest_index] = manifest_row

        for element, value in row.items():
            validate_element = find_col_element(element, self._manifest_metadata)
            df_manifest.loc[manifest_index, validate_element] = value

        self._manifest_metadata.save()

    def remove_values(self):
        """
        Future function
        """
        pass

    def save(self):
        """
        Save sample metadata file

        """
        self._metadata.save()