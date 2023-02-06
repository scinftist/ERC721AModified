// SPDX-License-Identifier: MIT
// ERC721A Contracts v4.2.3
// import "./ERC721ANew.sol";
import "./ERC721AModified.sol";

pragma solidity ^0.8.4;

contract ERC721AModifiedToken is ERC721AModified {
    constructor(address[] memory recivers, uint256[] memory amounts)
        ERC721AModified("ERC721A", "A")
    {
        require(
            recivers.length == amounts.length,
            "length of recivers and amounts does not match"
        );
        for (uint256 i = 0; i < recivers.length; i++) {
            _mintERC2309(recivers[i], amounts[i]);
        }
    }

    function mintSingle() public {
        _mint(msg.sender, 1);
    }

    function multiMint() public {
        _mint(msg.sender, 10);
    }

    function totMinted() public view returns (uint256) {
        return _totalMinted();
    }

    function burnThis(uint256 tokenId) public {
        _burn(tokenId, true);
    }
}
