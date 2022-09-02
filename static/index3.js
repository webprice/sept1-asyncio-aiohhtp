function loadTable() {
  Swal.fire(`Please wait, scraping in progress...`);
  const xhttp = new XMLHttpRequest();
  xhttp.open("GET", `${window.location.origin}/load_data`);
  xhttp.send();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      console.log(this.responseText);
      var trHTML = '';
      const objects = JSON.parse(this.responseText);
      for (let object of objects) {
        trHTML += '<tr>';
        trHTML += '<td>'+object['id']+'</td>';
        trHTML += '<td>'+object['title']+'</td>';
        trHTML += '<td>'+object['price']+'</td>';
        trHTML += '<td><img width="150px" src="'+object['photo']+'" class="avatar" /></td>';
        trHTML += '<td>'+object['seller']+'</td>';
        trHTML += '<td><button type="button" class="btn btn-outline-danger" onclick="userDelete('+object['id']+')">Del</button></td>';
        trHTML += "</tr>";
      }
      document.getElementById("mytable").innerHTML = trHTML;
    }
  };
}

function existingData() {

  const xhttp = new XMLHttpRequest();
  xhttp.open("GET", `${window.location.origin}/existing_data`);
  xhttp.send();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      console.log(this.responseText);
      var trHTML = '';
      const objects = JSON.parse(this.responseText);
      for (let object of objects) {
        trHTML += '<tr>';
        trHTML += '<td>'+object['id']+'</td>';
        trHTML += '<td>'+object['title']+'</td>';
        trHTML += '<td>'+object['price']+'</td>';
        trHTML += '<td><img width="150px" src="'+object['photo']+'" class="avatar" /></td>';
        trHTML += '<td>'+object['seller']+'</td>';
        trHTML += '<td><button type="button" class="btn btn-outline-danger" onclick="userDelete('+object['id']+')">Del</button></td>';
        trHTML += "</tr>";
      }
      document.getElementById("mytable").innerHTML = trHTML;
    }
  };
}

function userDelete(id) {
  const xhttp = new XMLHttpRequest();
  xhttp.open("GET", `${window.location.origin}/test_delete/${id}` );
  xhttp.send();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4) {
      const objects = JSON.parse(this.responseText);
      Swal.fire(`Item ${id} has been removed from the database`);
      existingData();
    }
  };
}







function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTable2");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

