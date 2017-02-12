import React from 'react';
import { shallow } from 'enzyme';

import { Page } from '../Model';
import Viewer from '../components/Viewer';

test('Blank page', () => {
  var p = new Page();
  expect(shallow(<Viewer revision={p.latestRevision} />).html()).toMatchSnapshot();
});

test('Empty revision', () => {
  expect(shallow(<Viewer />).html()).toMatchSnapshot();
});
