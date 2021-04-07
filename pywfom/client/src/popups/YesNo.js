import Modal from 'react-bootstrap/Modal';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';

export default function YesNo(props) {

  return(
    <div>{
        <div>
          <Modal.Header>
            <Modal.Title>{props.question}</Modal.Title>
          </Modal.Header>
          <Modal.Footer>
            <Button onClick={props.onNo} variant='secondary'>No</Button>
            <Button onClick={props.onYes}>Yes</Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
