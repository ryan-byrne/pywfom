import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Table from 'react-bootstrap/Table';

export default function LoadConfig(props){

  useEffect(() => {
    fetch('/api/file/default')
      .then( resp => { if (resp.ok) {return resp.json()} })
      .then( data => console.log(data))
  },[]);

  return(
    <div>{
        <div>
          <Modal.Header>
            <Modal.Title>Saved Configurations:</Modal.Title>
          </Modal.Header>
          <Modal.Footer>
            <Button variant="secondary" onClick={props.onHide}>Close</Button>
          </Modal.Footer>
        </div>
      }</div>
  )
}
