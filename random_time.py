from random import randrange
from datetime import datetime
import argparse
import csv

timestep_in_seconds = {
  'second': 1,
  'minute': 60,
  'hour': 3600,
  'day': 86400
}

class RandomTime:
  def validate_timerange(self, timerange, n=1, timestep=None, allow_dupes=False):
    '''
    Helper to validate timerange of datetime objects
    '''
    start = timerange['start']
    end = timerange['end']
    delta = (end - start).total_seconds()
    step = timestep_in_seconds.get(timestep, 1)
    unique_steps_in_range = delta/step + 1
    if start > end:
      raise ValueError('End datetime is before start datetime')

    if not allow_dupes and n > unique_steps_in_range:
      raise ValueError('Range is too small for %d UNIQUE timestamp(s)' % n)


  def get_timerange(self, start, end=None, timestep=None, allow_dupes=False):
    '''
    Helper to create a valid datetime range with start/end datetime objects
    '''
    now = datetime.now()
    try:
      start_dt = datetime.fromisoformat(start)
    except Exception:
      raise ValueError('Invalid start datetime string, must be ISO format')

    if not end:
      end_dt = now
    else:
      try:
        end_dt = datetime.fromisoformat(end)
      except Exception:
        raise ValueError('Invalid end datetime string, must be ISO format')

    return {
      'start': self.floor_time(start_dt, timestep),
      'end': self.floor_time(end_dt, timestep)
    }

  def floor_time(self, dt, step='second'):
    '''
    Helper to return datetime floor to timestep user gave
    '''
    units_to_floor = {
      'second': { 'microsecond': 0 },
      'minute': { 'second': 0, 'microsecond': 0 },
      'hour': { 'minute': 0, 'second': 0, 'microsecond': 0 },
      'day': { 'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0 }
    }

    return dt.replace(**units_to_floor.get(step, {}))

  def generate_one(self, start, end, timestep=None):
    '''
    Generate a single random timestamp within a datetime range
    Range has start and end timestamps
    Possible timestep: second, minute, hour, day
    '''
    step = timestep_in_seconds.get(timestep, 1)
    n = randrange(start, end, step)
    output = datetime.fromtimestamp(n)
    return output

  def generate_n(self, n, start, end=None, timestep=None, allow_dupes=False):
    '''
    Generate multipe(n) random timestamps within a datetime timerange
    '''
    output=[]
    # handles missing time inputs and validates timerange
    timerange = self.get_timerange(start, end, timestep)
    self.validate_timerange(timerange, n, timestep, allow_dupes)
    start_timestamp = int(timerange['start'].timestamp())
    end_timestamp = int(timerange['end'].timestamp())

    while len(output) < n:
      rand_dt = self.generate_one(
        start_timestamp,
        end_timestamp,
        timestep
      )
      if not allow_dupes and rand_dt in output:
        continue
      output.append(rand_dt)
    return output

def main():
  '''
  Handles command line args to generate n random timestamps in csv file

  Example command line
  > python random_time.py -h
  > python random_time.py test.csv 100 2020-01-01
  > python random_time.py test.csv 100 2019-01-01 --allow-dupes
  > python random_time.py test.csv 100 2020-01-01 -end 2020-01-31 -timestep day
  >
  '''
  # define command line arguments
  argparser = argparse.ArgumentParser(
    description='Generate csv file of random timestamps within a time range'
  )
  # required
  argparser.add_argument('csv_name', help='filename of csv to generate')
  argparser.add_argument('n', type=int, help='amount of random timestamps')
  argparser.add_argument(
    'start',
    help='ISO string start of time range, must be before now if no end given'
  )
  # optional
  argparser.add_argument(
    '-end', help='ISO string end of time range, default now'
  )
  argparser.add_argument(
    '-timestep',
    choices=['second', 'minute', 'hour', 'day'],
    help='increment of time unit, default second'
  )
  argparser.add_argument(
    '--allow-dupes',
    action='store_true',
    help='Flag to allow duplicate timestamps'
  )

  # run random time generator
  args = argparser.parse_args()
  rand_time = RandomTime()
  rand_time_list = rand_time.generate_n(
    args.n, args.start, args.end, args.timestep, args.allow_dupes
  )

  # write isoformat string to csv file
  output_file = args.csv_name #TODO: handle invalid or existing filename
  with open(output_file, 'w') as csv_file:
    writer = csv.writer(csv_file)
    for time in rand_time_list:
      writer.writerow([time.isoformat()])

  return output_file

if __name__ == '__main__':
    print('Generated: ' + main())

