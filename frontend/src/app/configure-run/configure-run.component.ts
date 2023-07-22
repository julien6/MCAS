import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-configure-run',
  templateUrl: './configure-run.component.html',
  styleUrls: ['./configure-run.component.css']
})
export class ConfigureRunComponent implements OnInit {

  firstFormGroup = this._formBuilder.group({
    firstCtrl: ['', Validators.required],
  });
  secondFormGroup = this._formBuilder.group({
    secondCtrl: ['', Validators.required],
  });
  isLinear = false;

  constructor(private _formBuilder: FormBuilder, public dialogRef: MatDialogRef<ConfigureRunComponent>) { }

  ngOnInit(): void {
  }

}
