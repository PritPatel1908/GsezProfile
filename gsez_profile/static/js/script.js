document.addEventListener('DOMContentLoaded', function () {
    // Company name suggestions for previous employer
    const previousEmployerNameInput = document.getElementById('id_previous_employer_name');
    if (previousEmployerNameInput) {
        previousEmployerNameInput.addEventListener('input', function () {
            const query = this.value;
            if (query.length >= 2) {
                fetch(`/api/company-suggestions/?query=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        const datalist = document.getElementById('company-suggestions');
                        if (!datalist) {
                            const newDatalist = document.createElement('datalist');
                            newDatalist.id = 'company-suggestions';
                            document.body.appendChild(newDatalist);
                            previousEmployerNameInput.setAttribute('list', 'company-suggestions');
                        } else {
                            datalist.innerHTML = '';
                        }

                        data.forEach(company => {
                            const option = document.createElement('option');
                            option.value = company;
                            document.getElementById('company-suggestions').appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error fetching company suggestions:', error));
            }
        });
    }

    // QR Code scanner for security personnel
    const scannerPreview = document.getElementById('scanner-preview');
    const scanButton = document.getElementById('scan-button');

    if (scannerPreview && scanButton) {
        scanButton.addEventListener('click', function () {
            // In a real application, you would use a library like instascan or html5-qrcode
            // For this demo, we'll simulate scanning by showing a form to enter user ID
            const userIdForm = document.createElement('div');
            userIdForm.innerHTML = `
                <form id="manual-scan-form" class="mt-3">
                    <div class="mb-3">
                        <label for="user_id" class="form-label">Enter User ID:</label>
                        <input type="text" class="form-control" id="user_id" name="user_id" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            `;

            scannerPreview.innerHTML = '';
            scannerPreview.appendChild(userIdForm);

            document.getElementById('manual-scan-form').addEventListener('submit', function (e) {
                e.preventDefault();
                const userId = document.getElementById('user_id').value;
                document.getElementById('scan-form').elements.user_id.value = userId;
                document.getElementById('scan-form').submit();
            });
        });
    }

    // Dynamic form fields for profile editing
    const addEmergencyContactBtn = document.getElementById('add-emergency-contact');
    if (addEmergencyContactBtn) {
        addEmergencyContactBtn.addEventListener('click', function () {
            const emergencyContactsContainer = document.getElementById('emergency-contacts-container');
            const contactCount = emergencyContactsContainer.children.length;

            const newContact = document.createElement('div');
            newContact.className = 'row mb-3';
            newContact.innerHTML = `
                <div class="col-md-5">
                    <input type="text" name="emergency_contact_name_${contactCount}" class="form-control" placeholder="Name">
                </div>
                <div class="col-md-5">
                    <input type="text" name="emergency_contact_number_${contactCount}" class="form-control" placeholder="Phone Number">
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-contact">Remove</button>
                </div>
            `;

            emergencyContactsContainer.appendChild(newContact);

            // Add event listener to the remove button
            newContact.querySelector('.remove-contact').addEventListener('click', function () {
                emergencyContactsContainer.removeChild(newContact);
            });
        });
    }

    // Similar functionality for family members, previous employers, and qualifications
    // would be implemented in a similar way
});

// Function to preview profile image before upload
function previewProfileImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            document.getElementById('profile-image-preview').src = e.target.result;
            document.getElementById('profile-image-preview').style.display = 'block';
        }

        reader.readAsDataURL(input.files[0]);
    }
}

// User form dynamic rows
function setupDynamicRows() {
    // Add Emergency Contact
    const addEmergencyContactBtn = document.getElementById('addEmergencyContact');
    if (addEmergencyContactBtn) {
        addEmergencyContactBtn.addEventListener('click', function () {
            const template = document.getElementById('emergencyContactTemplate');
            const container = document.getElementById('emergencyContactsContainer');
            const clone = template.content.cloneNode(true);

            // Add event listener to remove button
            const removeBtn = clone.querySelector('.remove-row');
            removeBtn.addEventListener('click', function () {
                this.closest('.emergency-contact-row').remove();
            });

            // Add some styling to differentiate the new row
            const newRow = clone.querySelector('.emergency-contact-row');
            newRow.classList.add('border-top', 'pt-3', 'mt-3');

            container.appendChild(clone);
        });
    }

    // Add Family Member
    const addFamilyMemberBtn = document.getElementById('addFamilyMember');
    if (addFamilyMemberBtn) {
        addFamilyMemberBtn.addEventListener('click', function () {
            const template = document.getElementById('familyMemberTemplate');
            const container = document.getElementById('familyMembersContainer');
            const clone = template.content.cloneNode(true);

            // Add event listener to remove button
            const removeBtn = clone.querySelector('.remove-row');
            removeBtn.addEventListener('click', function () {
                this.closest('.family-member-row').remove();
            });

            // Add some styling to differentiate the new row
            const newRow = clone.querySelector('.family-member-row');
            newRow.classList.add('border-top', 'pt-3', 'mt-3');

            container.appendChild(clone);
        });
    }

    // Add Previous Employer
    const addPreviousEmployerBtn = document.getElementById('addPreviousEmployer');
    if (addPreviousEmployerBtn) {
        addPreviousEmployerBtn.addEventListener('click', function () {
            const template = document.getElementById('previousEmployerTemplate');
            const container = document.getElementById('previousEmployersContainer');
            const clone = template.content.cloneNode(true);

            // Add event listener to remove button
            const removeBtn = clone.querySelector('.remove-row');
            removeBtn.addEventListener('click', function () {
                this.closest('.previous-employer-row').remove();
            });

            // Add some styling to differentiate the new row
            const newRow = clone.querySelector('.previous-employer-row');
            newRow.classList.add('border-top', 'pt-3');

            container.appendChild(clone);
        });
    }

    // Add Qualification
    const addQualificationBtn = document.getElementById('addQualification');
    if (addQualificationBtn) {
        addQualificationBtn.addEventListener('click', function () {
            const template = document.getElementById('qualificationTemplate');
            const container = document.getElementById('qualificationsContainer');
            const clone = template.content.cloneNode(true);

            // Add event listener to remove button
            const removeBtn = clone.querySelector('.remove-row');
            removeBtn.addEventListener('click', function () {
                this.closest('.qualification-row').remove();
            });

            // Add some styling to differentiate the new row
            const newRow = clone.querySelector('.qualification-row');
            newRow.classList.add('border-top', 'pt-3', 'mt-3');

            container.appendChild(clone);
        });
    }

    // Setup existing remove buttons for emergency contacts
    document.querySelectorAll('.remove-contact').forEach(button => {
        button.addEventListener('click', function () {
            const index = this.getAttribute('data-index');
            const row = this.closest('tr');
            row.remove();

            // Add hidden input to track deleted item
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'deleted_contacts[]';
            input.value = index;
            document.getElementById('deletedContactsContainer').appendChild(input);
        });
    });

    // Setup existing remove buttons for family members
    document.querySelectorAll('.remove-family-member').forEach(button => {
        button.addEventListener('click', function () {
            const index = this.getAttribute('data-index');
            const row = this.closest('tr');
            row.remove();

            // Add hidden input to track deleted item
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'deleted_family_members[]';
            input.value = index;
            document.getElementById('deletedFamilyMembersContainer').appendChild(input);
        });
    });

    // Setup existing remove buttons for previous employers
    document.querySelectorAll('.remove-employer').forEach(button => {
        button.addEventListener('click', function () {
            const index = this.getAttribute('data-index');
            const row = this.closest('tr');
            row.remove();

            // Add hidden input to track deleted item
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'deleted_employers[]';
            input.value = index;
            document.getElementById('deletedEmployersContainer').appendChild(input);
        });
    });

    // Setup existing remove buttons for qualifications
    document.querySelectorAll('.remove-qualification').forEach(button => {
        button.addEventListener('click', function () {
            const index = this.getAttribute('data-index');
            const row = this.closest('tr');
            row.remove();

            // Add hidden input to track deleted item
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'deleted_qualifications[]';
            input.value = index;
            document.getElementById('deletedQualificationsContainer').appendChild(input);
        });
    });

    // Setup existing remove-row buttons
    document.querySelectorAll('.remove-row').forEach(button => {
        button.addEventListener('click', function () {
            this.closest('[class$="-row"]').remove();
        });
    });
}

// Call the function when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    setupDynamicRows();
}); 