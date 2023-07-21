import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { Component, Input, TemplateRef, ViewChild } from '@angular/core';
import { LibraryElementComponent } from '../library-element/library-element.component';

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.css']
})
export class LibraryComponent {

  centered = false;
  disabled = false;
  unbounded = false;

  libraryConfigs: any;

  constructor(public dialogRef: MatDialogRef<LibraryComponent>, public dialog: MatDialog) {
    this.getLibraryInCache().then((value) => {
      this.libraryConfigs = this.getLibraryConfigs();
    }).catch((err) => console.error(err))
  }

  // TODO : to replace by real REST service call
  getLibraryConfigs() {
    const config = {
      title: "Small-scaled company network under two attacks",
      short_description: "A simple small-scaled company network containing Linux and Windows machines splitted into four subnets.",
      md_file: "description.md",
      thumbnail_file: "thumbnail.png",
      data_file: "data.json"
    }
    return {
      Agents: { "A001": config, "A002": config, "A003": config, "A004": config },
      Nodes: { "N001": config, "N002": config, "N003": config, "N004": config },
      Scenarios: { "S001": config, "S002": config, "S003": config, "S004": config }
    }
  }


  /* TODO: download the whole library in frontend cache asset folder from a REST service call */
  getLibraryInCache() {
    return new Promise<boolean>((resolve, reject) => {
      resolve(true);
    })
  }

  openLibraryElementDialog(elementType: string, elementId: string, descriptionFile: string) {
    this.dialog.open(LibraryElementComponent, {
      width: '100%',
      data: {
        title: this.libraryConfigs[elementType][elementId]["title"],
        md_file_path: '/assets/library/' + elementType.toLowerCase() + '/' + elementId + '/' + descriptionFile,
        data_file_path: '/assets/library/' + elementType.toLowerCase() + '/' + elementId + '/' + this.libraryConfigs[elementType][elementId]["data_file"]
      }
    });
  }

}
function $any(libraryIds: { Agents: string[]; Nodes: string[]; Scenarios: string[]; }) {
  throw new Error('Function not implemented.');
}

