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

  const handleStart = () => {
    fetch('/api/system/acquisition',{method:"POST"}).then(resp=>resp.json().then(data=>{
      if (resp.ok){

      } else {
        setMessage(
          <div>{
            <Alert variant="danger">
              <h3>Unable to Start Acquisition</h3>
              <p><b>Due to the Following errors:</b></p>
              <ul>
              {
                data.map(error=><li>{error}</li>)
              }
              </ul>
            </Alert>
          }</div>
        )
      }
    }));
  }

  useEffect(()=>{
    handleStart()
  },[])

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
            <Button onClick={handleStart}>Start</Button>
          </Row>
          {message}
        </Container>
      }</div>
  )
}
