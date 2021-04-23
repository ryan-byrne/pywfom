import {useEffect,useState} from 'react';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Image from 'react-bootstrap/Image';
import Alert from 'react-bootstrap/Alert';

export default function Acquisition(props){

  const [message, setMessage] = useState(null);
  const [acquiring, setAcquiring] = useState(false);

  const handleStop = () => {
    fetch('/api/system/acquisition', {method:'DELETE'})
      .then(resp=>{
        if (resp.ok){ props.setAcquiring(false) }
        else { resp.text().then(txt=>console.error(txt)) }
      })
  }

  return (
    <div>{
        <Container>
          <Row>
            {
              props.config.cameras.map((cam, idx)=> {
                return (
                  <Col>
                    <Image fluid src={`/api/feed/${idx}`}/>
                  </Col>
                )
              })
            }
          </Row>
          <Row>
            <Button variant="danger" onClick={handleStop}>
              {acquiring ? "Stop Acquisition" : "Exit"}
            </Button>
          </Row>
          {message}
        </Container>
      }</div>
  )
}
