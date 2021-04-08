import Container from 'react-bootstrap/Container';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';

export default function Error(props) {
  return (
    <div>{
        <Container className='mt-3'>
          <Alert variant="danger">
            <h1>
              Server Error
            </h1>
            <p>Unable to retrieve data from the <b>PyWFOM API</b>.</p>
            <ol>
              <li>Ensure <b>pywfom</b> is running</li>
              <li>Try <b>refreshing</b> the page <Button onClick={()=>window.location.reload()} size="sm">Refresh</Button></li>
              <li>Open a terminal and run <b>pywfom test</b> if the problem persists</li>
            </ol>

          </Alert>
        </Container>
      }</div>
  )
}
