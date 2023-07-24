import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-configure-run',
  templateUrl: './configure-run.component.html',
  styleUrls: ['./configure-run.component.css']
})
export class ConfigureRunComponent implements OnInit {

  firstFormGroup: FormGroup;

  fullSimulationFormGroup: FormGroup;
  fullEmulationFormGroup: FormGroup;
  select_number_of_iteration_per_episode: FormGroup;

  secondFormGroup: FormGroup;

  selectedMode: string;
  selectedSimulationEngine: string;
  selectedEmulationEngine: string;
  selectedNumIterPerEp: number;
  selectedNumEp: number;

  constructor(private _formBuilder: FormBuilder, public dialogRef: MatDialogRef<ConfigureRunComponent>) {
    this.selectedMode = "";
    this.selectedSimulationEngine = "";
    this.selectedEmulationEngine = "";
    this.selectedNumIterPerEp = 0;
    this.selectedNumEp = 0;
  }

  ngOnInit(): void {

    this.firstFormGroup = new FormGroup({
      select_mode: new FormControl(null, Validators.required),
    });

    this.fullSimulationFormGroup = new FormGroup({
      select_simulation_engine: new FormControl(null, Validators.required),
      select_number_of_iteration_per_episode: new FormControl(null, Validators.required),
      select_number_of_episode: new FormControl(null, Validators.required),
    });

    this.fullEmulationFormGroup = new FormGroup({
      select_emulation_engine: new FormControl(null, Validators.required),
    });

    this.secondFormGroup = new FormGroup({
      secondCtrl: new FormControl(null, Validators.required),
    });

  }

  onSelectingMode(value: any) {
    this.selectedMode = value;
  }

  onSelectingSimulationEngine(value: any) {
    this.selectedSimulationEngine = value;
  }

  onSelectingNumIterPerEp(value: any) {
    this.selectedNumIterPerEp = value;
  }

  onSelectingEmulationEngine(value: any) {
    this.selectedEmulationEngine = value;
  }

  onSelectingNumEp(value: any) {
    this.selectedNumEp = value;
  }

}
