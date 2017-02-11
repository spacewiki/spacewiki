import fetchMock from 'fetch-mock';
import { Page } from '../Model';

fetchMock.get('*', new Page().data);
fetchMock.post('*', new Page().data);

/*export default function fetch(url, options) {
  return new Promise((resolve, reject) => {
    resolve({
      ok: true,
      json() {
        return {};
      }
    });
  });
}

global.fetch = fetch;*/
