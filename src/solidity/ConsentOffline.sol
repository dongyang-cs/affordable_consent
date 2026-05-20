// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8;
import "./ConsentBase.sol";

contract ConsentCode is ConsentBase {
    //  constructor() {
    //     dataProvider = msg.sender;
    // }

 
    // MARK: - Terms
    struct Terms {
        // baseline
        string Area_URI;
        bytes32 Area_Hash;

        string Disease_URI;
        bytes32 Disease_Hash;
 
    }

    mapping(address => Terms) providerMapping; // data subject
    mapping(address => Terms) requesterMapping; // data subject

    mapping(uint8 => uint8[]) Country_Group_Code_Mapping_Baseline;

    // MARK: - UploadTerms
    function TermsByRole(
        uint8 role,
        address _address
    ) private view returns (Terms storage) {
        if (role == ROLE_PROVIDER) {
            // require(msg.sender == dataProvider, "TermsByRole: Invalid sender");
            return providerMapping[_address];
        } else if (role == ROLE_REQUESTER) {
            return requesterMapping[_address];
        } else {
            revert("TermsByRole: Invalid role specified");
        }
    }


    // MARK: - UploadAreaBaseline
    function UploadArea(
        uint8 role,
        address _address,
        string memory Area_URI,
        bytes32 Area_Hash
    ) public {
        Terms storage terms = TermsByRole(role, _address);
            terms.Area_URI = Area_URI;
            terms.Area_Hash = Area_Hash;
       
    }

    function delete_area(
        uint8 role,
        address _address
    ) public {
        Terms storage terms = TermsByRole(role, _address);

        delete terms.Area_URI;
        delete terms.Area_Hash;
    }

    // MARK: UploadDiseaseBaseline
    function UploadDisease(
        uint8 role,
        address _address,
        string memory Disease_URI,
        bytes32 Disease_Hash
    ) public {
        Terms storage terms = TermsByRole(role, _address);

               terms.Disease_URI = Disease_URI;
        terms.Disease_Hash = Disease_Hash;
  
    }

    // MARK: UploadDiseaseBaseline
    function delete_disease(
        uint8 role,
        address _address
    ) public {
        Terms storage terms = TermsByRole(role, _address);

        delete terms.Disease_URI;
        delete terms.Disease_Hash;
    }

    // MARK: - CheckAreaBaseline
    function CheckArea(
        address _provider,
        address _requester
    ) public view override returns (bool) {
        

        return true;
    }

    // MARK: - CheckDisease
    function CheckDisease(
        address _provider_address,
        address _requester_address
    ) public view override returns (bool) {
        
        return true;
    }

    function access_data(address provider_address, address requester_address) view public override returns (uint32) {

        uint32 result = super.basic_access_check(provider_address, requester_address);
        return result;
    }
}
