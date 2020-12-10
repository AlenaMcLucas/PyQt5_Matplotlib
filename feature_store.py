import pandas as pd


def data_type_check(user_input):
    """Check that a user has input a valid field classification."""
    if user_input in ('categorical', 'quantitative', '?'):
        return user_input
    else:
        return None


class FeatureStore:

    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(self.path)
        self.col_map = []
        self.auto_map()

    def __str__(self):
        return self.path + "\n" + str(self.col_map)

    def auto_map(self):
        """Automatically classifies each field by data type."""
        self.col_map = [(col, 'categorical') if self.df[col].dtype == object else
                        (col, 'quantitative') if self.df[col].dtype in [int, float] else
                        (col, '?') for col in self.df.columns]

    def override_map(self, new_map):
        """Overrides automatic classification of each field.

        Parameters
        ----------
        new_map : lst of tuples
            column_name (str), assignment (str)
        """
        new_map_check = {key: value for (key, value) in new_map.items() if data_type_check(value) is not None}

        self.col_map = [(item[0], new_map_check.get(item[0])) if new_map_check.get(item[0], None) is not None else item
                        for item in self.col_map]

    def save(self, file_name):
        self.df.to_csv(f'data/{file_name}.csv', index=False)


if __name__ == '__main__':
    fs = FeatureStore('data/test-data.csv')
    print(fs)
    fs.override_map({'sex': 'categorical'})
    print(fs)
    fs.save('edit_v1')
