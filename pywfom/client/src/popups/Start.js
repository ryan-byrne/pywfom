import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';

export default function Start(props){

  return(
    <div>{
        <div>
          <Modal.Body>
            <Modal.Title>Start Acquisition?</Modal.Title>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={props.onHide}>No</Button>
            <Button>Yes</Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
