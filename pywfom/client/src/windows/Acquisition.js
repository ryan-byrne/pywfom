import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Image from 'react-bootstrap/Image';

export default function Acquisition(props){

  const handleStop = () => {
    fetch('/api/acquisition', {method:'DELETE'})
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
                    <Image fluid src={'/api/feed/'+cam.id}/>
                  </Col>
                )
              })
            }
          </Row>
          <Button variant="danger" onClick={handleStop}>Stop Acquisition</Button>
        </Container>
      }</div>
  )
}
