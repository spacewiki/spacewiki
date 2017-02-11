import React from 'react';
import { shallow } from 'enzyme';
import App from '../components/App';

jest.mock('whatwg-fetch');

test('App smoke test', () => {
  const app = shallow(<App />);
});
