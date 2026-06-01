// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SmartGarden {

    struct Record {
        uint256 timestamp;
        string  dataHash;
        uint256 soilAvg;
        uint256 pumpCount;
        string  aiDecision;
    }

    Record[] public records;
    address  public owner;

    event DataRecorded(
        uint256 indexed id,
        uint256 indexed timestamp,
        string  dataHash,
        string  aiDecision
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    function recordData(
        string memory _dataHash,
        uint256 _soilAvg,
        uint256 _pumpCount,
        string memory _aiDecision
    ) public onlyOwner {
        uint256 id = records.length;
        records.push(Record({
            timestamp:  block.timestamp,
            dataHash:   _dataHash,
            soilAvg:    _soilAvg,
            pumpCount:  _pumpCount,
            aiDecision: _aiDecision
        }));
        emit DataRecorded(id, block.timestamp, _dataHash, _aiDecision);
    }

    function getRecordCount() public view returns (uint256) {
        return records.length;
    }

    function getRecord(uint256 index) public view returns (
        uint256 timestamp,
        string memory dataHash,
        uint256 soilAvg,
        uint256 pumpCount,
        string memory aiDecision
    ) {
        require(index < records.length, "Index out of range");
        Record memory r = records[index];
        return (r.timestamp, r.dataHash, r.soilAvg, r.pumpCount, r.aiDecision);
    }

    function verifyHash(uint256 index, string memory _hash)
        public view returns (bool) {
        require(index < records.length, "Index out of range");
        return keccak256(bytes(records[index].dataHash)) ==
               keccak256(bytes(_hash));
    }
}
