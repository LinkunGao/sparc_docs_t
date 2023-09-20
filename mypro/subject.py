"""Subject module documentation"""
class Subject:
    count = 0
    _dataset_path = Path('./')
    _metadata = None

    def __init__(self):

        self.subject_id = ""
        self.subject_dir = Path()
        self.index = -1
        self._samples = {}
        self._generate_subject_path_and_id()

    def get_sample(self, sample_sds_id) -> Sample:
        """
        Provide the sample sds id to query a sample for edit

        :param sample_sds_id: the sample id in sds
        :return: Sample
        """
        if not isinstance(sample_sds_id, str):
            msg = f"Sample not found, please provide an string sample_sds_id!, you sample_sds_id type is {type(sample_sds_id)}"
            raise ValueError(msg)

        try:
            sample = self._samples.get(sample_sds_id)
            return sample
        except:
            msg = f"Sample not found with {sample_sds_id}! Please check your subject_sds_id in subject metadata file"
            raise ValueError(msg)

    def _generate_subject_path_and_id(self):
        """
        generate subject id and path in dataset

        """
        primary_dir = self._dataset_path.joinpath("primary")
        if primary_dir.exists():
            sub_dirs = []
            for sub_dir in primary_dir.iterdir():
                if sub_dir.is_dir():
                    sub_dirs.append(sub_dir.name)
            while True:
                Subject.count += 1
                self.subject_id = f"sub-{Subject.count}"
                if self.subject_id not in sub_dirs:
                    break
        else:
            Subject.count += 1
            self.subject_id = f"sub-{Subject.count}"
        self.subject_dir = primary_dir.joinpath(self.subject_id)
        self._add_subject_row()

    def add_samples(self, samples):
        """
        Add samples into subject object

        :param samples: a samples list
        :type samples: list
        """
        if isinstance(samples, list):
            for sample in samples:
                if isinstance(sample, Sample):
                    self._create_sample(sample)
                    self._samples[sample.sample_id] = sample
        elif isinstance(samples, Sample):
            self._create_sample(samples)
            self._samples[samples.sample_id] = samples

    def _create_sample(self, sample):
        """
        Generate sample id and subject id in sample class
        :param sample: a sample object
        :type sample: Sample
        """
        sample.set_subject_id(self.subject_id)

    def _add_subject_row(self):
        """
        Add row in subject metadata file

        """
        df = self._metadata.data
        if self.subject_id in df['subject id']:
            self.index = df.loc[df['subject id'] == self.subject_id].index[0]
        else:
            subject = [self.subject_id] + [float('nan')] * (len(df.columns) - 1)
            # Create new row
            self.index = len(df)
            df.loc[self.index] = subject

    def set_values(self, metadata={}):
        """
        :param metadata: key : value dict (element:value)
        :type metadata: dict
        """
        if not isinstance(metadata, dict):
            msg = f"You should use a dict here, you provide parameter type is {type(metadata)}"
            raise TypeError(msg)

        for element, value in metadata.items():
            if element == 'subject id':
                continue
            else:
                self.set_value(element, value)

    def set_value(self, element, value):
        """
        Set value for one element for a subject

        :param element: element in sample metadata file
        :type element: str
        :param value: the values for that element
        :type value: str|int
        """
        df = self._metadata.data
        index = df.loc[df['subject id'] == self.subject_id].index[0]
        element = find_col_element(element, self._metadata)
        if index == self.index:
            df.loc[index, element] = value

        self.save()

    def move(self):
        for sample in self._samples.values():
            sample.move()

    def remove_values(self):
        pass

    def save(self):
        self._metadata.save()
